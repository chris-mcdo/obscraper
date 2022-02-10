"""Fetch multiple objects and place them in containers.

Also perform exception handling and logging.
"""

import logging
from functools import partial

import httpx
import trio

from . import _assemble, _exceptions

logger = logging.getLogger(__name__)


async def fetch(results, label, func, obj_type=None):
    """Fetch result and place in container.

    The return value of ``func`` is placed in the ``results`` dict,
    under the dict key ``label``. ``obj_name`` (optional) gives the type
    of the object (e.g. post) returned by ``func`` (this is used for
    logging only).

    If you want to pass arguments to ``func``, use a functools.partial
    object.

    Parameters
    ----------
    results : dict
        A container to store the result of the function call.
    label : str
        A label (dict key) for the result.
    func : callable
        An async function whose return value should be added to the
        results.
    obj_type : str, optional
        The type of object returned by the function call. Used for
        logging.
    """
    log_info = {"label": label, "obj": obj_type}

    try:
        obj = await func()
        logger.info("Successfully grabbed %(obj)s %(label)s", log_info)
    except _exceptions.InvalidResponseError:
        obj = None
        logger.info(
            "InvalidResponseError raised when grabbing" " %(obj)s %(label)s", log_info
        )
    except _exceptions.AttributeNotFoundError:
        obj = None
        logger.warning(
            "AttributeNotFoundError raised when grabbing" " %(obj)s %(label)s", log_info
        )

    if label in results.keys():
        logger.warning(
            "Results container already contains an entry" "for post %(obj)s %(label)s",
            log_info,
        )

    results[label] = obj


async def fetch_posts(names_dict):
    """Get list of posts."""
    results = {}
    async with httpx.AsyncClient() as async_client:
        async with trio.open_nursery() as nursery:
            for label, name in names_dict.items():
                assembler = partial(_assemble.assemble_post, async_client, name)
                fetcher = partial(fetch, results, label, assembler, "post")
                nursery.start_soon(fetcher)
    return results


async def fetch_vote_counts(vote_ids_dict):
    """Get list of vote counts."""
    results = {}
    async with httpx.AsyncClient() as async_client:
        async with trio.open_nursery() as nursery:
            for label, vote_id in vote_ids_dict.items():
                assembler = partial(
                    _assemble.assemble_vote_count, async_client, vote_id
                )
                fetcher = partial(fetch, results, label, assembler, "vote count")
                nursery.start_soon(fetcher)
    return results


async def fetch_comment_counts(comment_ids_dict):
    """Get list of comment counts."""
    results = {}
    async with httpx.AsyncClient() as async_client:
        async with trio.open_nursery() as nursery:
            for label, comment_id in comment_ids_dict.items():
                assembler = partial(
                    _assemble.assemble_comment_count, async_client, comment_id
                )
                fetcher = partial(fetch, results, label, assembler, "comment count")
                nursery.start_soon(fetcher)
    return results


async def fetch_edit_dates():
    """Get list of edit dates."""
    results = {}
    async with httpx.AsyncClient() as async_client:
        async with trio.open_nursery() as nursery:
            assembler = partial(_assemble.assemble_edit_dates, async_client)
            fetcher = partial(fetch, results, "edit-dates", assembler, "edit dates")
            nursery.start_soon(fetcher)
    return results["edit-dates"]


async def fetch_vote_auth():
    """Get vote auth code."""
    results = {}
    async with httpx.AsyncClient() as async_client:
        async with trio.open_nursery() as nursery:
            assembler = partial(_assemble.assemble_vote_auth, async_client)
            fetcher = partial(fetch, results, "vote-auth", assembler, "vote auth")
            nursery.start_soon(fetcher)
    return results["vote-auth"]
