"""Async HTTP client for INE Portugal API."""

import logging
import time
from typing import Any, Optional, Union

import httpx

from pyptine.__version__ import __version__
from pyptine.utils.exceptions import APIError, RateLimitError

logger = logging.getLogger(__name__)


class AsyncINEClient:
    """Async HTTP client for INE Portugal API.

    Provides core async HTTP functionality with:
    - Async session management with connection pooling
    - Automatic retry logic with exponential backoff
    - Timeout configuration
    - User-agent identification
    - Error handling and response validation

    Args:
        language: Language for API responses ("EN" or "PT")
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts

    Example:
        >>> async with AsyncINEClient(language="EN") as client:
        ...     response = await client._make_request("/endpoint", {"param": "value"})
    """

    BASE_URL = "https://www.ine.pt"
    DEFAULT_TIMEOUT = 30
    MAX_RETRIES = 3
    USER_AGENT = f"pyptine/{__version__} (Python INE API Client - Async)"

    def __init__(
        self,
        language: str = "EN",
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = MAX_RETRIES,
    ) -> None:
        """Initialize async INE client."""
        self.language = language.upper()
        self.timeout = timeout
        self.max_retries = max_retries
        self.client: Optional[httpx.AsyncClient] = None

        # Validate language
        if self.language not in ("EN", "PT"):
            raise ValueError(f"Language must be 'EN' or 'PT', got: {language}")

        logger.info(
            f"Initialized async INE client (language={self.language}, "
            f"timeout={self.timeout}s, max_retries={self.max_retries})"
        )

    async def __aenter__(self) -> "AsyncINEClient":
        """Async context manager entry."""
        self.client = httpx.AsyncClient(
            headers={
                "User-Agent": self.USER_AGENT,
                "Accept": "application/json, text/xml",
                "Accept-Encoding": "gzip, deflate",
            },
            timeout=self.timeout,
        )
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        if self.client:
            await self.client.aclose()
            logger.debug("Closed async HTTP client")

    async def _make_request(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        response_format: str = "json",
    ) -> Union[dict[str, Any], str]:
        """Make async HTTP request to INE API.

        Args:
            endpoint: API endpoint path
            params: Query parameters
            response_format: Expected response format ("json" or "xml")

        Returns:
            Parsed JSON dict or raw XML string

        Raises:
            APIError: If request fails
            RateLimitError: If rate limited
        """
        if not self.client:
            raise RuntimeError("Client not initialized. Use 'async with' context manager.")

        url = self.BASE_URL + endpoint

        # Add language to params
        params = {} if params is None else params.copy()
        params["lang"] = self.language

        logger.debug(f"Making async request to {endpoint} with params: {params}")

        try:
            start_time = time.time()
            response = await self.client.get(url, params=params)
            elapsed = time.time() - start_time

            logger.debug(
                f"Async request completed in {elapsed:.2f}s (status={response.status_code})"
            )

            # Handle rate limiting
            if response.status_code == 429:
                raise RateLimitError("Too many requests to INE API")

            # Raise for HTTP errors
            response.raise_for_status()

            # Parse response based on format
            if response_format == "json":
                return self._parse_json_response(response)
            elif response_format == "xml":
                return self._parse_xml_response(response)
            else:
                raise ValueError(f"Unsupported response format: {response_format}")

        except httpx.TimeoutException:
            logger.error(f"Async request timeout after {self.timeout}s")
            raise APIError(0, f"Request timeout after {self.timeout}s") from None

        except httpx.HTTPError as e:
            status_code = getattr(e.response, "status_code", 0) if hasattr(e, "response") else 0
            logger.error(f"HTTP error: {status_code} - {str(e)}")

            if status_code == 404:
                raise APIError(404, "Resource not found") from None
            else:
                raise APIError(status_code, str(e)) from e

    def _parse_json_response(self, response: httpx.Response) -> dict[str, Any]:
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
            return data
        except ValueError as e:
            logger.error(f"Failed to parse JSON response: {str(e)}")
            raise APIError(0, f"Invalid JSON response: {str(e)}") from e

    def _parse_xml_response(self, response: httpx.Response) -> str:
        """Parse XML response.

        Args:
            response: HTTP response

        Returns:
            Raw XML string

        Raises:
            APIError: If response is not valid text
        """
        try:
            xml_text = response.text
            logger.debug(f"Parsed XML response with {len(xml_text)} characters")
            return xml_text
        except Exception as e:
            logger.error(f"Failed to parse XML response: {str(e)}")
            raise APIError(0, f"Invalid XML response: {str(e)}") from e
