"""Custom exceptions for pyine package."""


class INEError(Exception):
    """Base exception for INE package."""

    pass


class APIError(INEError):
    """API request failed.

    Raised when an HTTP request to the INE API fails.
    """

    def __init__(self, status_code: int, message: str) -> None:
        """Initialize APIError.

        Args:
            status_code: HTTP status code
            message: Error message
        """
        self.status_code = status_code
        self.message = message
        super().__init__(f"API Error {status_code}: {message}")


class InvalidIndicatorError(INEError):
    """Indicator code is invalid or not found.

    Raised when an indicator code doesn't exist in the INE system.
    """

    pass


class DimensionError(INEError):
    """Invalid dimension filter.

    Raised when dimension codes or values are invalid.
    """

    pass


class CacheError(INEError):
    """Cache operation failed.

    Raised when there's an error with cache read/write operations.
    """

    pass


class RateLimitError(APIError):
    """API rate limit exceeded.

    Raised when too many requests have been made to the API.
    """

    def __init__(self, message: str = "Rate limit exceeded") -> None:
        """Initialize RateLimitError.

        Args:
            message: Error message
        """
        super().__init__(429, message)


class ValidationError(INEError):
    """Input validation failed.

    Raised when user input doesn't meet requirements.
    """

    pass


class DataProcessingError(INEError):
    """Error processing data response.

    Raised when there's an error transforming API data.
    """

    pass
