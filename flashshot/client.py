"""FlashShot API client."""

import time
from typing import Any, Dict, List, Optional, Sequence, Union

import requests

from .exceptions import FlashShotError
from .types import (
    BalanceResponse,
    BatchScreenshotResponse,
    ScreenshotOptions,
    ScreenshotResponse,
    UsageResponse,
)

_DEFAULT_BASE_URL = "https://api.flashshot.dev"
_DEFAULT_TIMEOUT = 60
_MAX_RETRIES = 2
_INITIAL_BACKOFF = 1.0


class FlashShot:
    """Client for the FlashShot Screenshot API.

    Args:
        api_key: Your FlashShot API key (``sk_live_...`` or ``sk_test_...``).
        base_url: Override the default API base URL.
        timeout: Request timeout in seconds (default 60).
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        *,
        base_url: str = _DEFAULT_BASE_URL,
        timeout: int = _DEFAULT_TIMEOUT,
    ) -> None:
        if not api_key:
            raise FlashShotError(
                "api_key is required",
                code="missing_api_key",
            )
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._session = requests.Session()
        self._session.headers.update(
            {
                "x-api-key": self._api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "flashshot-python/1.0.0",
            }
        )

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def screenshot(
        self,
        url: str,
        *,
        format: Optional[str] = None,
        full_page: Optional[bool] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        device_scale_factor: Optional[float] = None,
        device: Optional[str] = None,
        quality: Optional[int] = None,
        wait_for: Optional[Union[str, int]] = None,
        include_analysis: Optional[bool] = None,
        cookies: Optional[List[Dict[str, str]]] = None,
        headers: Optional[Dict[str, str]] = None,
        basic_auth: Optional[Dict[str, str]] = None,
        custom_css: Optional[str] = None,
        custom_js: Optional[str] = None,
        block_cookies: Optional[bool] = None,
        block_ads: Optional[bool] = None,
        cache_ttl: Optional[int] = None,
        stealth: Optional[bool] = None,
        webhook_url: Optional[str] = None,
    ) -> ScreenshotResponse:
        """Capture a screenshot of a single URL.

        Args:
            url: The webpage URL to capture.
            format: Image format (``"png"``, ``"jpeg"``, ``"webp"``).
            full_page: Capture the full scrollable page.
            width: Viewport width in pixels.
            height: Viewport height in pixels.
            device_scale_factor: Device pixel ratio.
            device: Emulate a device (e.g. ``"iPhone 15"``).
            quality: Image quality 0-100 (JPEG/WebP only).
            wait_for: CSS selector or milliseconds to wait before capture.
            include_analysis: Include AI analysis of the page.
            cookies: List of cookie dicts to set before capture.
            headers: Extra HTTP headers for the page request.
            basic_auth: Dict with ``username`` and ``password`` keys.
            custom_css: CSS to inject into the page.
            custom_js: JavaScript to execute before capture.
            block_cookies: Block third-party cookies.
            block_ads: Block ads and trackers.
            cache_ttl: Cache time-to-live in seconds.
            stealth: Enable stealth mode to avoid bot detection.
            webhook_url: URL to receive a webhook when capture completes.

        Returns:
            A dict containing ``success``, ``data``, and ``usage``.

        Raises:
            FlashShotError: If the API returns an error.
        """
        options = _build_options(
            format=format,
            full_page=full_page,
            width=width,
            height=height,
            device_scale_factor=device_scale_factor,
            device=device,
            quality=quality,
            wait_for=wait_for,
            include_analysis=include_analysis,
            cookies=cookies,
            headers=headers,
            basic_auth=basic_auth,
            custom_css=custom_css,
            custom_js=custom_js,
            block_cookies=block_cookies,
            block_ads=block_ads,
            cache_ttl=cache_ttl,
            stealth=stealth,
            webhook_url=webhook_url,
        )
        body: Dict[str, Any] = {"url": url}
        if options:
            body["options"] = options
        return self._request("POST", "/api/v1/screenshot", json=body)

    def batch(
        self,
        urls: Sequence[str],
        *,
        format: Optional[str] = None,
        full_page: Optional[bool] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        device_scale_factor: Optional[float] = None,
        device: Optional[str] = None,
        quality: Optional[int] = None,
        wait_for: Optional[Union[str, int]] = None,
        include_analysis: Optional[bool] = None,
        cookies: Optional[List[Dict[str, str]]] = None,
        headers: Optional[Dict[str, str]] = None,
        basic_auth: Optional[Dict[str, str]] = None,
        custom_css: Optional[str] = None,
        custom_js: Optional[str] = None,
        block_cookies: Optional[bool] = None,
        block_ads: Optional[bool] = None,
        cache_ttl: Optional[int] = None,
        stealth: Optional[bool] = None,
        webhook_url: Optional[str] = None,
    ) -> BatchScreenshotResponse:
        """Capture screenshots of multiple URLs in one request.

        Accepts the same options as :meth:`screenshot`; they apply to all
        URLs in the batch.

        Args:
            urls: Sequence of webpage URLs to capture.

        Returns:
            A dict containing ``success``, ``data`` (list), and ``usage``.

        Raises:
            FlashShotError: If the API returns an error.
        """
        options = _build_options(
            format=format,
            full_page=full_page,
            width=width,
            height=height,
            device_scale_factor=device_scale_factor,
            device=device,
            quality=quality,
            wait_for=wait_for,
            include_analysis=include_analysis,
            cookies=cookies,
            headers=headers,
            basic_auth=basic_auth,
            custom_css=custom_css,
            custom_js=custom_js,
            block_cookies=block_cookies,
            block_ads=block_ads,
            cache_ttl=cache_ttl,
            stealth=stealth,
            webhook_url=webhook_url,
        )
        body: Dict[str, Any] = {"urls": list(urls)}
        if options:
            body["options"] = options
        return self._request("POST", "/api/v1/screenshots/batch", json=body)

    def balance(self) -> BalanceResponse:
        """Retrieve current plan, usage, and quota.

        Returns:
            A dict with ``plan`` and ``usage`` keys.

        Raises:
            FlashShotError: If the API returns an error.
        """
        return self._request("GET", "/api/v1/balance")

    def usage(self, *, limit: Optional[int] = None) -> UsageResponse:
        """Retrieve usage history.

        Args:
            limit: Maximum number of records to return.

        Returns:
            A dict with a ``usage`` key containing a list of records.

        Raises:
            FlashShotError: If the API returns an error.
        """
        params: Dict[str, Any] = {}
        if limit is not None:
            params["limit"] = limit
        return self._request("GET", "/api/v1/usage", params=params)

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Send an HTTP request with automatic retry on 429 and 5xx errors."""
        url = self._base_url + path
        last_exc: Optional[Exception] = None

        for attempt in range(_MAX_RETRIES + 1):
            try:
                resp = self._session.request(
                    method,
                    url,
                    json=json,
                    params=params,
                    timeout=self._timeout,
                )
            except requests.RequestException as exc:
                raise FlashShotError(
                    f"Request failed: {exc}",
                    code="request_error",
                ) from exc

            # Success
            if resp.status_code < 400:
                return resp.json()

            # Rate limited -- respect Retry-After header
            if resp.status_code == 429:
                retry_after = _parse_retry_after(resp)
                if attempt < _MAX_RETRIES:
                    time.sleep(retry_after)
                    continue
                raise _error_from_response(resp)

            # Server error -- exponential backoff
            if resp.status_code >= 500:
                if attempt < _MAX_RETRIES:
                    time.sleep(_INITIAL_BACKOFF * (2 ** attempt))
                    continue
                raise _error_from_response(resp)

            # Client error (4xx, not 429) -- no retry
            raise _error_from_response(resp)

        # Should not reach here, but just in case
        raise _error_from_response(resp)  # type: ignore[possibly-undefined]


# ------------------------------------------------------------------ #
# Module-level helpers
# ------------------------------------------------------------------ #


def _build_options(**kwargs: Any) -> Dict[str, Any]:
    """Build an options dict, dropping ``None`` values."""
    return {k: v for k, v in kwargs.items() if v is not None}


def _parse_retry_after(resp: requests.Response) -> float:
    """Extract a wait time in seconds from the Retry-After header."""
    header = resp.headers.get("Retry-After")
    if header is not None:
        try:
            return max(float(header), 0.5)
        except (ValueError, TypeError):
            pass
    return 1.0


def _error_from_response(resp: requests.Response) -> FlashShotError:
    """Create a ``FlashShotError`` from an HTTP error response."""
    try:
        body = resp.json()
    except (ValueError, KeyError):
        body = {}

    message = (
        body.get("error", {}).get("message")
        or body.get("message")
        or body.get("error")
        or resp.text
        or f"HTTP {resp.status_code}"
    )
    code = (
        body.get("error", {}).get("code")
        or body.get("code")
        or "api_error"
    )
    return FlashShotError(
        message=str(message),
        code=str(code),
        status_code=resp.status_code,
    )
