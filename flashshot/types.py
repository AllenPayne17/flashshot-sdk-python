"""Type definitions for FlashShot SDK (Python 3.8+ compatible)."""

import sys
from typing import Any, Dict, List, Optional, Sequence, Union

if sys.version_info >= (3, 8):
    from typing import TypedDict
else:
    from typing_extensions import TypedDict


class BasicAuth(TypedDict, total=False):
    username: str
    password: str


class Cookie(TypedDict, total=False):
    name: str
    value: str
    domain: str
    path: str


class ScreenshotOptions(TypedDict, total=False):
    """Options for screenshot capture."""

    format: str
    full_page: bool
    width: int
    height: int
    device_scale_factor: float
    device: str
    quality: int
    wait_for: Union[str, int]
    include_analysis: bool
    cookies: List[Cookie]
    headers: Dict[str, str]
    basic_auth: BasicAuth
    custom_css: str
    custom_js: str
    block_cookies: bool
    block_ads: bool
    cache_ttl: int
    stealth: bool
    webhook_url: str


class ScreenshotData(TypedDict, total=False):
    """Data returned from a screenshot capture."""

    image_url: str
    overview: str
    description: str
    render_time_ms: int
    format: str
    width: int
    height: int


class UsageInfo(TypedDict, total=False):
    """Usage information returned with API responses."""

    screenshots_used: int
    screenshots_limit: int
    period: str


class ScreenshotResponse(TypedDict):
    """Response from the screenshot endpoint."""

    success: bool
    data: ScreenshotData
    usage: UsageInfo


class BatchScreenshotResponse(TypedDict):
    """Response from the batch screenshot endpoint."""

    success: bool
    data: List[ScreenshotData]
    usage: UsageInfo


class BalanceResponse(TypedDict):
    """Response from the balance endpoint."""

    plan: str
    usage: UsageInfo


class UsageRecord(TypedDict, total=False):
    """A single usage history record."""

    url: str
    timestamp: str
    render_time_ms: int
    format: str
    cached: bool


class UsageResponse(TypedDict):
    """Response from the usage endpoint."""

    usage: List[UsageRecord]
