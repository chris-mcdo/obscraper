"""Assemble the results of downloading and tidying data.

This module exists mainly to cache results of responses.

This interface is internal - implementation details may change.
"""

import functools
import time
import threading

import cachetools
import cachetools.keys
import cachetools.func

from . import _download, _tidy


def async_assembly_cache(maxsize, ttl, timer=time.monotonic, getsizeof=None):
    """Custom TTL cache for the ``assemble`` functions.

    Differs from the ``cachetools`` default by implementing (1) a
    (thread-safe) ``cache_clear`` method, and (2) ignoring the
    ``async_client`` argument. This lets it store results across
    sessions.
    """
    def custom_cache(func):
        # Define cache
        cache = cachetools.TTLCache(maxsize=maxsize, ttl=ttl, timer=timer,
                                    getsizeof=getsizeof)
        lock = threading.Lock()

        # Define hash key generator
        def assembly_hashkey(async_client, *args, **kwargs):
            """Hash key for the ``assemble`` functions.

            It ignores their ``async_client`` argument.
            """
            return cachetools.keys.hashkey(*args, **kwargs)

        # Define wrapper
        # Inpsired by https://github.com/tkem/cachetools/issues/92
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            key = assembly_hashkey(*args, **kwargs)
            try:
                with lock:
                    return cache[key]
            except KeyError:
                pass
            val = await func(*args, **kwargs)
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
async def assemble_post(async_client, name):
    """Download and tidy a post."""
    raw_response = await _download.download_post(name, async_client)
    tidy_item = _tidy.tidy_post(raw_response)
    return tidy_item


@async_assembly_cache(maxsize=5000, ttl=3600)
async def assemble_vote_count(async_client, vote_id, vote_auth):
    """Download and tidy a vote count."""
    raw_response = await _download.download_vote_count(vote_id, vote_auth,
                                                       async_client)
    tidy_item = _tidy.tidy_vote_count(raw_response)
    return tidy_item


@async_assembly_cache(maxsize=5000, ttl=3600)
async def assemble_comment_count(async_client, comment_id):
    """Download and tidy a comment count."""
    raw_response = await _download.download_comment_count(comment_id,
                                                          async_client)
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
    raw_response = await _download.download_post(
        _download.VOTE_AUTH_UPDATE_NAME, async_client)
    tidy_item = _tidy.tidy_vote_auth(raw_response)
    return tidy_item
