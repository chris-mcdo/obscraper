"""Download data from external APIs and return raw responses.

This interface is internal - implementation details may change.
"""
import functools

import httpx
import trio

from . import _exceptions
from ._extract_post import name_to_url

INCREASE_FACTOR = 2
MAX_DELAY = 5
MAX_REQUESTS = 10

VOTE_API_URL = (
    "https://www.overcomingbias.com/" "wp-content/plugins/gd-star-rating/ajax.php"
)
COMMENT_API_URL = "https://overcoming-bias.disqus.com/count-data.js"
EDIT_DATES_URL = "https://www.overcomingbias.com/post.xml"


def async_retry(start_delay):
    """Either return a 2xx response, try again, or raise an error."""

    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            delay = start_delay
            for _ in range(MAX_REQUESTS):
                response = await func(*args, **kwargs)
                if response.status_code != 429:
                    break
                try:
                    delay = int(response.headers["Retry-After"])
                except (KeyError, TypeError):
                    delay = delay * INCREASE_FACTOR
                if delay > MAX_DELAY:
                    raise _exceptions.InvalidResponseError("Exceeded max timeout.")
                await trio.sleep(delay)

            try:
                response.raise_for_status()
            except httpx.HTTPStatusError as err:
                raise _exceptions.InvalidResponseError("Invalid response.") from err
            return response

        return wrapper

    return decorator


@async_retry(start_delay=0.04)
async def download_post(async_client, name):
    """Download a post by its name."""
    headers = get_default_headers()
    url = name_to_url(name)
    response = await async_client.get(url, headers=headers)
    return response


@async_retry(start_delay=0.04)
async def download_vote_count(async_client, number, vote_auth):
    """Download vote count for a post."""
    headers = get_default_headers()
    headers.update({"x-requested-with": "XMLHttpRequest"})
    params = {
        "_ajax_nonce": vote_auth,
        "vote_type": "cache",
        "vote_domain": "a",
        "votes": f"atr.{number}",
    }
    response = await async_client.post(VOTE_API_URL, headers=headers, params=params)
    return response


@async_retry(start_delay=0.001)
async def download_comment_count(async_client, disqus_id):
    """Download comment count for a post."""
    headers = get_default_headers()
    params = {"1": disqus_id}
    response = await async_client.post(COMMENT_API_URL, headers=headers, params=params)
    return response


@async_retry(start_delay=0.001)
async def download_edit_dates(async_client):
    """Download list of posts and edit dates."""
    headers = get_default_headers()
    response = await async_client.get(EDIT_DATES_URL, headers=headers)
    return response


def get_default_headers():
    """Get headers to be used with all requests."""
    return {"user-agent": "Mozilla/5.0"}
