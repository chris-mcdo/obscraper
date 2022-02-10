"""Assemble downloaded data into a tidy format.

This module exists mainly to cache results of responses.

This interface is internal - implementation details may change.
"""

import functools
import threading
import time

import cachetools
import cachetools.func
import cachetools.keys

from . import _download, _tidy

# Name used to update the vote auth code
VOTE_AUTH_UPDATE_NAME = "/2011/12/life-is-good"


def async_assembly_cache(maxsize, ttl, timer=time.monotonic, getsizeof=None):
    """Custom TTL cache for the `assemble` functions.

    Differs from the `cachetools` default by implementing a thread-safe
    `cache_clear` method, and ignoring the `async_client` argument. This lets it
    store results across sessions.

    And it's asynchronous.
    """

    def custom_cache(func):
        # Define cache
        cache = cachetools.TTLCache(
            maxsize=maxsize, ttl=ttl, timer=timer, getsizeof=getsizeof
        )
        lock = threading.Lock()

        # Define wrapper
        # Inpsired by https://github.com/tkem/cachetools/issues/92
        @functools.wraps(func)
        async def wrapper(async_client, *args, **kwargs):
            # Hash key ignores `async_client`, so that results are
            # cached across sessions.
            key = cachetools.keys.hashkey(*args, **kwargs)
            try:
                with lock:
                    return cache[key]
            except KeyError:
                pass
            val = await func(async_client, *args, **kwargs)
            # in case of a race, prefer the item already in the cache
            try:
                with lock:
                    return cache.setdefault(key, val)
            except ValueError:
                pass  # value too large
            return val

        # Define cache clear method
        def cache_clear():
            with lock:
                cache.clear()

        wrapper.cache_clear = cache_clear

        return wrapper

    return custom_cache


@async_assembly_cache(maxsize=5000, ttl=3600)
async def assemble_post(async_client, name, votes=True, comments=True, edit_dates=True):
    """Download and tidy a post."""
    raw_response = await _download.download_post(async_client, name)
    post = _tidy.tidy_post(raw_response)

    if votes:
        post.votes = await assemble_vote_count(async_client, post.number)

    if comments:
        post.comments = await assemble_comment_count(async_client, post.disqus_id)

    if edit_dates:
        edit_dates = await assemble_edit_dates(async_client)
        post.edit_date = edit_dates[post.name]

    return post


@async_assembly_cache(maxsize=5000, ttl=3600)
async def assemble_vote_count(async_client, number):
    """Download and tidy a vote count."""
    vote_auth = await assemble_vote_auth(async_client)
    raw_response = await _download.download_vote_count(async_client, number, vote_auth)
    tidy_item = _tidy.tidy_vote_count(raw_response)
    return tidy_item


@async_assembly_cache(maxsize=5000, ttl=3600)
async def assemble_comment_count(async_client, disqus_id):
    """Download and tidy a comment count."""
    raw_response = await _download.download_comment_count(async_client, disqus_id)
    tidy_item = _tidy.tidy_comment_count(raw_response)
    return tidy_item


@async_assembly_cache(maxsize=1, ttl=300)
async def assemble_edit_dates(async_client):
    """Download and tidy the list of edit dates."""
    raw_response = await _download.download_edit_dates(async_client)
    tidy_item = _tidy.tidy_edit_dates(raw_response)
    return tidy_item


@async_assembly_cache(maxsize=1, ttl=43200)
async def assemble_vote_auth(async_client):
    """Download and tidy the vote auth code."""
    raw_response = await _download.download_post(async_client, VOTE_AUTH_UPDATE_NAME)
    tidy_item = _tidy.tidy_vote_auth(raw_response)
    return tidy_item
