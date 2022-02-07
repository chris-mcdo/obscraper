"""Download data from external APIs and return raw responses.

This interface is internal - implementation details may change.
"""
import functools
import random
import asyncio

from ._extract_post import name_to_url

START_DELAY = 0.04
INCREASE_FACTOR = 4
MAX_DELAY = 3
MAX_REQUESTS = 5

VOTE_API_URL = ('https://www.overcomingbias.com/'
                'wp-content/plugins/gd-star-rating/ajax.php')
COMMENT_API_URL = 'https://overcoming-bias.disqus.com/count-data.js'
EDIT_DATES_URL = 'https://www.overcomingbias.com/post.xml'


def async_retry_request(func):
    """Retry HTTP request until 429 response is no longer received."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        delay = START_DELAY
        for _ in range(MAX_REQUESTS):
            response = await func(*args, **kwargs)
            if response.status_code != 429:
                break
            try:
                delay = int(response.headers['Retry-After'])
            except (KeyError, TypeError):
                delay = delay * (1 + random.random()) / 2
            if delay > MAX_DELAY:
                break
            await asyncio.sleep(delay)
            delay = delay * INCREASE_FACTOR
        return response
    return wrapper


@async_retry_request
async def download_post(name, async_client):
    """Download a post by its name."""
    headers = get_default_headers()
    url = name_to_url(name)
    response = await async_client.get(url, headers=headers)
    return response


@async_retry_request
async def download_vote_count(vote_id, vote_auth, async_client):
    """Download vote count for a post."""
    headers = get_default_headers()
    headers.update({'x-requested-with': 'XMLHttpRequest'})
    params = {
        '_ajax_nonce': vote_auth,
        'vote_type': 'cache',
        'vote_domain': 'a',
        'votes': vote_id
    }
    response = await async_client.post(VOTE_API_URL, headers=headers,
                                       params=params)
    return response


@async_retry_request
async def download_comment_count(comment_id, async_client):
    """Download comment count for a post."""
    headers = get_default_headers()
    params = {'1': comment_id}
    response = await async_client.post(COMMENT_API_URL, headers=headers,
                                       params=params)
    return response


@async_retry_request
async def download_edit_dates(async_client):
    """Download list of posts and edit dates."""
    headers = get_default_headers()
    response = await async_client.get(EDIT_DATES_URL, headers=headers)
    return response


def get_default_headers():
    """Get headers to be used with all requests."""
    return {'user-agent': 'Mozilla/5.0'}
