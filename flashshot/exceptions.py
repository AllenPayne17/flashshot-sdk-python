"""FlashShot exception classes."""


class FlashShotError(Exception):
    """Exception raised when the FlashShot API returns an error.

    Attributes:
        message: Human-readable error description.
        code: Machine-readable error code (e.g. "rate_limited", "invalid_url").
        status_code: HTTP status code from the API response.
    """

    def __init__(
        self,
        message: str,
        code: str = "unknown_error",
        status_code: int = 0,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code

    def __repr__(self) -> str:
        return (
            f"FlashShotError(message={self.message!r}, "
            f"code={self.code!r}, status_code={self.status_code})"
        )
