"""Base HTTP client for INE Portugal API."""

import logging
import time
from pathlib import Path
from typing import Any, Optional, Union, cast

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from pyptine.__version__ import __version__
from pyptine.cache.disk import DiskCache
from pyptine.utils.exceptions import APIError, RateLimitError

logger = logging.getLogger(__name__)

# Import cache - delay to avoid circular imports
_disk_cache = None


def _get_disk_cache() -> type[DiskCache]:
    """Lazy import of DiskCache to avoid circular imports."""
    global _disk_cache
    if _disk_cache is None:
        from pyptine.cache.disk import DiskCache

        _disk_cache = DiskCache
    return _disk_cache


class INEClient:
    """Base client for INE Portugal API.

    Provides core HTTP functionality including:
    - Session management with connection pooling
    - Automatic retry logic with exponential backoff
    - Timeout configuration
    - User-agent identification
    - Error handling and response validation

    Args:
        language: Language for API responses ("EN" or "PT")
        timeout: Request timeout in seconds
        cache_enabled: Enable HTTP caching
        cache_dir: Directory for cache storage
        max_retries: Maximum number of retry attempts

    Example:
        >>> client = INEClient(language="EN")
        >>> response = client._make_request("/endpoint", {"param": "value"})
    """

    BASE_URL = "https://www.ine.pt"
    DEFAULT_TIMEOUT = 30
    MAX_RETRIES = 3
    USER_AGENT = f"pyptine/{__version__} (Python INE API Client)"

    def __init__(
        self,
        language: str = "EN",
        timeout: int = DEFAULT_TIMEOUT,
        cache_enabled: bool = True,
        cache_dir: Optional[Path] = None,
        max_retries: int = MAX_RETRIES,
    ) -> None:
        """Initialize INE client."""
        self.language = language.upper()
        self.timeout = timeout
        self.cache_enabled = cache_enabled
        self.cache_dir = cache_dir
        self.max_retries = max_retries
        self.cache = None

        # Validate language
        if self.language not in ("EN", "PT"):
            raise ValueError(f"Language must be 'EN' or 'PT', got: {language}")

        # Initialize cache if enabled
        if self.cache_enabled:
            disk_cache = _get_disk_cache()
            self.cache = disk_cache(cache_dir=cache_dir)
            logger.debug(f"Cache enabled at: {self.cache.get_cache_dir()}")

        # Initialize session
        self.session = self._create_session()

        logger.info(
            f"Initialized INE client (language={self.language}, "
            f"cache={self.cache_enabled}, timeout={self.timeout}s)"
        )

    def _create_session(self) -> requests.Session:
        """Create HTTP session with retry configuration.

        Returns:
            Configured requests Session
        """
        session = requests.Session()

        # Configure retry strategy
        # Note: 429 is not in the list - we handle rate limiting explicitly
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,  # Exponential backoff: {backoff factor} * (2 ** ({retry} - 1))
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"],
        )

        # Mount adapter with retry strategy
        adapter = HTTPAdapter(max_retries=retry_strategy, pool_connections=10, pool_maxsize=20)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Set headers
        session.headers.update(
            {
                "User-Agent": self.USER_AGENT,
                "Accept": "application/json, text/xml",
                "Accept-Encoding": "gzip, deflate",
            }
        )

        return cast(requests.Session, session)

    def _get_session_for_endpoint(self, endpoint: str) -> requests.Session:
        """Get appropriate session for endpoint.

        Args:
            endpoint: API endpoint path

        Returns:
            Cached or regular session based on endpoint and cache settings
        """
        if not self.cache_enabled or self.cache is None:
            return cast(requests.Session, self.session)

        # Use data cache for data endpoint
        if "pindica.jsp" in endpoint:
            return cast(requests.Session, self.cache.get_data_session())

        # Use metadata cache for metadata and catalogue endpoints
        elif "pindicaMeta.jsp" in endpoint or "xml_indic.jsp" in endpoint:
            return cast(requests.Session, self.cache.get_metadata_session())

        # Default to regular session for unknown endpoints
        else:
            return cast(requests.Session, self.session)

    def _make_request(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        response_format: str = "json",
        progress_callback: Optional[Any] = None,
    ) -> Union[dict[str, Any], str]:
        """Make HTTP request to INE API.

        Args:
            endpoint: API endpoint path (e.g., "/ine/json_indicador/pindica.jsp")
            params: Query parameters
            response_format: Expected response format ("json" or "xml")
            progress_callback: Optional callback function(downloaded_bytes, total_bytes)

        Returns:
            Parsed JSON dict or raw XML string

        Raises:
            APIError: If request fails
            RateLimitError: If rate limited
        """
        url = self.BASE_URL + endpoint

        # Add language to params
        params = {} if params is None else params.copy()
        params["lang"] = self.language

        logger.debug(f"Making request to {endpoint} with params: {params}")

        # Select appropriate session (cached or regular)
        session = self._get_session_for_endpoint(endpoint)

        try:
            start_time = time.time()

            # Use streaming if progress callback is provided
            # Note: Disable cache for streaming to get real-time progress
            if progress_callback is not None:
                # Use raw session (not cached) for progress tracking
                raw_session = self.session
                response = raw_session.get(url, params=params, timeout=self.timeout, stream=True)

                # Handle rate limiting
                if response.status_code == 429:
                    raise RateLimitError("Too many requests to INE API")

                # Raise for HTTP errors
                response.raise_for_status()

                # Get total size from headers
                total_size = int(response.headers.get("content-length", 0))
                downloaded = 0
                chunks = []

                # Report initial state
                progress_callback(0, total_size)

                # Download in chunks and report progress
                chunk_size = 8192
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:
                        chunks.append(chunk)
                        downloaded += len(chunk)
                        progress_callback(downloaded, total_size)

                # Combine chunks
                content = b"".join(chunks)
                response._content = content

            else:
                response = session.get(url, params=params, timeout=self.timeout)

            elapsed = time.time() - start_time

            # Check if response was from cache
            from_cache = getattr(response, "from_cache", False)
            cache_status = "from cache" if from_cache else "from API"
            logger.debug(
                f"Request completed in {elapsed:.2f}s ({cache_status}, "
                f"status={response.status_code})"
            )

            # Handle rate limiting (for non-streaming requests)
            if response.status_code == 429:
                raise RateLimitError("Too many requests to INE API")

            # Raise for HTTP errors (for non-streaming requests)
            if not progress_callback:
                response.raise_for_status()

            # Parse response based on format
            if response_format == "json":
                return self._parse_json_response(response)
            elif response_format == "xml":
                return self._parse_xml_response(response)
            else:
                raise ValueError(f"Unsupported response format: {response_format}")

        except requests.Timeout:
            logger.error(f"Request timeout after {self.timeout}s")
            raise APIError(0, f"Request timeout after {self.timeout}s") from None

        except requests.HTTPError as e:
            status_code = e.response.status_code if e.response is not None else 0
            logger.error(f"HTTP error: {status_code} - {str(e)}")

            if status_code == 404:
                raise APIError(404, "Resource not found") from None
            else:
                raise APIError(status_code, str(e)) from e

        except requests.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise APIError(0, f"Network error: {str(e)}") from e

    def _parse_json_response(self, response: requests.Response) -> dict[str, Any]:
        """Parse JSON response.

        Args:
            response: HTTP response

        Returns:
            Parsed JSON dictionary

        Raises:
            APIError: If JSON parsing fails
        """
        try:
            data = response.json()
            logger.debug(f"Parsed JSON response with {len(str(data))} characters")
            return cast(dict[str, Any], data)
        except ValueError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            raise APIError(0, f"Invalid JSON response: {str(e)}") from e

    def _parse_xml_response(self, response: requests.Response) -> str:
        """Parse XML response.

        Args:
            response: HTTP response

        Returns:
            Raw XML string

        Raises:
            APIError: If response is not valid text
        """
        try:
            xml_text = cast(str, response.text)
            logger.debug(f"Parsed XML response with {len(xml_text)} characters")
            return xml_text
        except Exception as e:
            logger.error(f"Failed to parse XML response: {str(e)}")
            raise APIError(0, f"Invalid XML response: {str(e)}") from e

    def is_catalogue_cached_on_disk(self) -> bool:
        """Check if catalogue data is cached on disk.

        Returns:
            True if catalogue is in disk cache
        """
        if not self.cache_enabled or self.cache is None:
            return False
        return self.cache.has_catalogue_cached()

    def close(self) -> None:
        """Close HTTP session and cleanup resources.

        Should be called when the client is no longer needed.
        """
        if self.session:
            self.session.close()
            logger.debug("Closed HTTP session")

        if self.cache:
            self.cache.close()
            logger.debug("Closed cache sessions")

    def __enter__(self) -> "INEClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()
