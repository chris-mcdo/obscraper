import logging
from io import StringIO

import httpx
import pytest

from examples import INVALID_SPECIAL_CASES, STANDARD_EXAMPLES, VALID_SPECIAL_CASES
from obscraper import _scrape


@pytest.fixture(scope="session")
def standard_examples():
    return _scrape.get_posts_by_names(list(STANDARD_EXAMPLES.keys()))


@pytest.fixture(scope="session")
def special_cases():
    return _scrape.get_posts_by_names(VALID_SPECIAL_CASES + INVALID_SPECIAL_CASES)


@pytest.fixture(scope="session")
def edit_dates():
    return _scrape.get_edit_dates()


@pytest.fixture(scope="session")
def http_client():
    client = httpx.Client(headers={"user-agent": "Mozilla/5.0"})
    yield client
    client.close()


@pytest.fixture
async def async_http_client():
    async with httpx.AsyncClient(headers={"user-agent": "Mozilla/5.0"}) as async_client:
        yield async_client


@pytest.fixture
def logs():
    # Log setup
    logger = logging.getLogger("obscraper")
    logger.setLevel(logging.DEBUG)
    logs = StringIO()
    formatter = logging.Formatter("%(levelname)s %(message)s")
    handler = logging.StreamHandler(logs)
    handler.formatter = formatter
    logger.addHandler(handler)

    yield logs

    # Log teardown
    logger.removeHandler(handler)
    logger.setLevel(logging.WARNING)
    handler.close()
