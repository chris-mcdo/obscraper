from unittest.mock import AsyncMock

import pytest
import trio

from obscraper._assemble import async_assembly_cache

# Maxsize and TTL are implemented by cachetools - no need to test here
# Just check that hashing and cache_clear work as expected


@pytest.fixture
def expensive_mock():
    async def return_async_client(async_client, *args, **kwargs):
        await trio.sleep(5)
        return async_client

    return AsyncMock(side_effect=return_async_client)


async def test_hash_ignores_first_arg_but_not_others(expensive_mock, autojump_clock):
    # Arrange
    @async_assembly_cache(maxsize=10, ttl=100)
    async def get_expensive_mock(async_client, *args, **kwargs):
        return await expensive_mock(async_client, *args, **kwargs)

    # Call for first time - miss
    start_time = trio.current_time()
    result = await get_expensive_mock("Client 1", "other args", also="keywords")
    assert trio.current_time() - start_time == 5
    assert result == "Client 1"
    assert expensive_mock.call_count == 1

    # Call with same args - hit
    start_time = trio.current_time()
    result = await get_expensive_mock("Client 1", "other args", also="keywords")
    assert trio.current_time() - start_time == 0
    assert result == "Client 1"
    assert expensive_mock.call_count == 1

    # Call with different first arg - hit
    start_time = trio.current_time()
    result = await get_expensive_mock("Client 2", "other args", also="keywords")
    assert trio.current_time() - start_time == 0
    assert result == "Client 1"
    assert expensive_mock.call_count == 1

    # Call with different positional args - miss
    start_time = trio.current_time()
    result = await get_expensive_mock("Client 3", "different arg")
    assert trio.current_time() - start_time == 5
    assert result == "Client 3"
    assert expensive_mock.call_count == 2


async def test_cache_clear_clears_cache(expensive_mock, autojump_clock):
    # Arrange
    @async_assembly_cache(maxsize=10, ttl=100)
    async def get_expensive_mock(async_client, *args, **kwargs):
        return await expensive_mock(async_client, *args, **kwargs)

    # Call for first time - miss
    start_time = trio.current_time()
    result = await get_expensive_mock("Client 1", "other args", also="keywords")
    assert trio.current_time() - start_time == 5
    assert result == "Client 1"
    assert expensive_mock.call_count == 1

    # Call with different first arg - hit
    start_time = trio.current_time()
    result = await get_expensive_mock("Client 2", "other args", also="keywords")
    assert trio.current_time() - start_time == 0
    assert result == "Client 1"
    assert expensive_mock.call_count == 1

    # Clear cache
    get_expensive_mock.cache_clear()

    # Call with different first arg - miss
    start_time = trio.current_time()
    result = await get_expensive_mock("Client 2", "other args", also="keywords")
    assert trio.current_time() - start_time == 5
    assert result == "Client 2"
    assert expensive_mock.call_count == 2
