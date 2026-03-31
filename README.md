# FlashShot Python SDK

The official Python client for the [FlashShot Screenshot API](https://flashshot.dev).

[![PyPI version](https://img.shields.io/pypi/v/flashshot.svg)](https://pypi.org/project/flashshot/)
[![Python versions](https://img.shields.io/pypi/pyversions/flashshot.svg)](https://pypi.org/project/flashshot/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

---

## What is FlashShot?

FlashShot is a fast, reliable screenshot API that captures pixel-perfect images of any webpage. It supports full-page captures, device emulation, stealth mode for bot-protected sites, ad and tracker blocking, custom CSS/JS injection, and optional AI-powered page analysis. The API is designed for developers who need high-quality, automated web screenshots at scale.

## Installation

```bash
pip install flashshot
```

Or with Poetry:

```bash
poetry add flashshot
```

## Quick Start

```python
from flashshot import FlashShot

client = FlashShot(api_key="sk_live_...")

response = client.screenshot("https://example.com")
print(response["data"]["image_url"])
```

## Configuration

The `FlashShot` client accepts the following constructor options:

| Parameter  | Type  | Default                       | Description                                       |
| ---------- | ----- | ----------------------------- | ------------------------------------------------- |
| `api_key`  | `str` | **required**                  | Your API key (`sk_live_...` or `sk_test_...`).    |
| `base_url` | `str` | `https://api.flashshot.dev`   | Override the default API base URL.                |
| `timeout`  | `int` | `60`                          | Request timeout in seconds.                       |

```python
client = FlashShot(
    api_key="sk_live_...",
    base_url="https://api.flashshot.dev",
    timeout=30,
)
```

## Methods

### `screenshot(url, **options)`

Capture a screenshot of a single URL.

```python
response = client.screenshot(
    "https://example.com",
    format="webp",
    full_page=True,
    width=1440,
    quality=90,
)

print(response["data"]["image_url"])
print(response["data"]["render_time_ms"])
print(response["usage"]["screenshots_used"])
```

### `batch(urls, **options)`

Capture screenshots of multiple URLs in a single request. All options are applied uniformly to every URL in the batch.

```python
response = client.batch(
    [
        "https://example.com",
        "https://example.org",
        "https://example.net",
    ],
    format="png",
    width=1280,
)

for item in response["data"]:
    print(item["image_url"])
```

### `balance()`

Retrieve your current plan, usage count, and quota limit.

```python
info = client.balance()

print(info["plan"])                        # e.g. "pro"
print(info["usage"]["screenshots_used"])   # e.g. 842
print(info["usage"]["screenshots_limit"])  # e.g. 5000
```

### `usage(limit=N)`

Retrieve your recent usage history.

```python
history = client.usage(limit=10)

for record in history["usage"]:
    print(record["url"], record["timestamp"], record["cached"])
```

## Screenshot Options

Both `screenshot()` and `batch()` accept the following keyword arguments:

| Option                | Type             | Default | Description                                                                      |
| --------------------- | ---------------- | ------- | -------------------------------------------------------------------------------- |
| `format`              | `str`            | `"png"` | Image format: `"png"`, `"jpeg"`, or `"webp"`.                                   |
| `full_page`           | `bool`           | `False` | Capture the full scrollable page instead of just the viewport.                   |
| `width`               | `int`            | `1280`  | Viewport width in pixels.                                                        |
| `height`              | `int`            | `800`   | Viewport height in pixels.                                                       |
| `device_scale_factor` | `float`          | `1.0`   | Device pixel ratio (e.g. `2.0` for Retina displays).                             |
| `device`              | `str`            | `None`  | Emulate a device preset (see [Device Presets](#device-presets)).                  |
| `quality`             | `int`            | `80`    | Image quality 0--100 (JPEG and WebP only).                                       |
| `wait_for`            | `str \| int`     | `None`  | CSS selector to wait for, or milliseconds to delay before capture.               |
| `include_analysis`    | `bool`           | `False` | Include an AI-generated overview and description of the page.                    |
| `cookies`             | `list[dict]`     | `None`  | Cookies to set before capture. Each dict: `name`, `value`, `domain`, `path`.     |
| `headers`             | `dict[str, str]` | `None`  | Extra HTTP headers to send with the page request.                                |
| `basic_auth`          | `dict`           | `None`  | HTTP Basic Auth credentials: `{"username": "...", "password": "..."}`.            |
| `custom_css`          | `str`            | `None`  | CSS to inject into the page before capture.                                      |
| `custom_js`           | `str`            | `None`  | JavaScript to execute on the page before capture.                                |
| `block_cookies`       | `bool`           | `False` | Block third-party cookies.                                                       |
| `block_ads`           | `bool`           | `False` | Block ads and trackers.                                                          |
| `cache_ttl`           | `int`            | `None`  | Cache time-to-live in seconds. Subsequent identical requests return cached image. |
| `stealth`             | `bool`           | `False` | Enable stealth mode to bypass bot detection.                                     |
| `webhook_url`         | `str`            | `None`  | URL to receive a POST callback when the capture completes.                       |

## Error Handling

All API errors are raised as `FlashShotError` with three attributes:

| Attribute     | Type  | Description                                                              |
| ------------- | ----- | ------------------------------------------------------------------------ |
| `message`     | `str` | Human-readable error description.                                        |
| `code`        | `str` | Machine-readable code (e.g. `"rate_limited"`, `"invalid_url"`).          |
| `status_code` | `int` | HTTP status code from the API response (e.g. `429`, `401`).             |

```python
from flashshot import FlashShot
from flashshot.exceptions import FlashShotError

client = FlashShot(api_key="sk_live_...")

try:
    response = client.screenshot("https://example.com")
except FlashShotError as e:
    print(f"Error: {e.message}")
    print(f"Code:  {e.code}")
    print(f"HTTP:  {e.status_code}")
```

## Auto-Retry

The client automatically retries failed requests for transient errors:

- **429 Too Many Requests** -- retries after the duration specified by the `Retry-After` response header (falls back to 1 second).
- **5xx Server Errors** -- retries with exponential backoff (1 s, 2 s).

A maximum of **2 retries** are attempted before raising a `FlashShotError`. Client errors (4xx other than 429) are never retried.

## Type Hints

The SDK ships with full type definitions via `TypedDict` classes. Editors and type checkers like mypy and pyright provide autocompletion and validation out of the box.

```python
from flashshot import FlashShot
from flashshot.types import ScreenshotResponse, ScreenshotOptions

client = FlashShot(api_key="sk_live_...")

response: ScreenshotResponse = client.screenshot("https://example.com")
image_url: str = response["data"]["image_url"]
```

Available types:

- `ScreenshotOptions` -- all capture options
- `ScreenshotResponse` -- single screenshot result
- `BatchScreenshotResponse` -- batch screenshot result
- `BalanceResponse` -- plan and quota info
- `UsageResponse` -- usage history
- `UsageRecord` -- single history entry
- `ScreenshotData` -- image URL, dimensions, render time
- `UsageInfo` -- screenshots used, limit, and period
- `BasicAuth` -- username and password dict
- `Cookie` -- name, value, domain, and path dict

## Device Presets

Pass a device name to the `device` option to emulate its viewport size and pixel ratio:

| Device          | Viewport    | Scale  |
| --------------- | ----------- | ------ |
| `iPhone 14`     | 390 x 844  | 3x     |
| `iPhone 15 Pro` | 393 x 852  | 3x     |
| `Pixel 7`       | 412 x 915  | 2.625x |
| `iPad Pro`      | 1024 x 1366 | 2x    |
| `Galaxy S23`    | 360 x 780  | 3x     |

```python
response = client.screenshot("https://example.com", device="iPhone 15 Pro")
```

## Examples

### Screenshot with AI analysis

```python
response = client.screenshot(
    "https://example.com",
    include_analysis=True,
)

print(response["data"]["overview"])
print(response["data"]["description"])
```

### Mobile device screenshot

```python
response = client.screenshot(
    "https://example.com",
    device="iPhone 15 Pro",
    full_page=True,
    format="webp",
)

print(response["data"]["image_url"])
```

### Screenshot with stealth mode

```python
response = client.screenshot(
    "https://bot-protected-site.com",
    stealth=True,
    wait_for=3000,
)

print(response["data"]["image_url"])
```

### HTML to image

```python
response = client.screenshot(
    "data:text/html,<h1>Hello World</h1>",
    width=800,
    height=600,
)

print(response["data"]["image_url"])
```

### Webhook callback

```python
response = client.screenshot(
    "https://example.com",
    webhook_url="https://your-server.com/webhooks/screenshot",
)
# The API sends a POST request to your webhook URL when capture completes.
```

### Disable ads and cookies blocking

```python
response = client.screenshot(
    "https://example.com",
    block_ads=True,
    block_cookies=True,
)
```

### Authenticated page with custom headers

```python
response = client.screenshot(
    "https://internal.example.com/dashboard",
    basic_auth={"username": "admin", "password": "secret"},
    headers={"X-Custom-Header": "value"},
    cookies=[
        {"name": "session", "value": "abc123", "domain": ".example.com", "path": "/"},
    ],
)
```

### Injecting custom CSS and JavaScript

```python
response = client.screenshot(
    "https://example.com",
    custom_css="body { background: #0d1117; color: #c9d1d9; }",
    custom_js="document.querySelector('.banner')?.remove();",
)
```

## License

MIT -- see [LICENSE](LICENSE) for details.

## Links

- [Website](https://flashshot.dev)
- [Documentation](https://docs.flashshot.dev)
- [Dashboard](https://dashboard.flashshot.dev)
- [PyPI Package](https://pypi.org/project/flashshot/)
