class TinyError(Exception):
    """Base for all tiny-py errors."""


class TinyAPIError(TinyError):
    """The API returned status != OK. Business-level error — do not retry."""

    def __init__(self, message: str, endpoint: str, errors: list[str]) -> None:
        super().__init__(message)
        self.endpoint = endpoint
        self.errors = errors


class TinyAuthError(TinyAPIError):
    """Invalid or expired token."""


class TinyRateLimitError(TinyError):
    """HTTP 429 received after all retry attempts are exhausted."""


class TinyServerError(TinyError):
    """HTTP 5xx after all retry attempts are exhausted."""


class TinyTimeoutError(TinyError):
    """Request timed out after all retry attempts."""
