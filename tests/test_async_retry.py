from unittest.mock import AsyncMock, Mock, patch

import pytest
import trio

from obscraper import _download, _exceptions

START_DELAY = 0.01
RETRY_AFTER = 2


class MockException(Exception):
    pass


def fail_n_times_then_succeed(n, success_code=200, fail_code=429, header=False):
    """Function which fails n times before succeeding."""
    failure = Mock(status_code=fail_code)
    # Need to mock httpx.HTTPStatusError in tests
    failure.raise_for_status.side_effect = MockException()
    success = Mock(status_code=success_code)
    if header:
        failure.headers = {"Retry-After": str(RETRY_AFTER)}

    mock_method = AsyncMock(side_effect=n * [failure] + [success])

    @_download.async_retry(START_DELAY)
    async def mock_responder():
        response = await mock_method()
        return response

    return mock_responder


async def test_retry_can_succeed_first_time(autojump_clock):
    fail_zero_times = fail_n_times_then_succeed(0)
    start_time = trio.current_time()
    response = await fail_zero_times()
    duration = trio.current_time() - start_time
    assert duration == 0
    assert response.status_code == 200


async def test_retry_succeeds_after_a_few_unsuccessful_tries(autojump_clock):
    fail_two_times = fail_n_times_then_succeed(2)
    response = await fail_two_times()
    assert response.status_code == 200


async def test_retry_gives_up_after_max_tries(autojump_clock):
    fail_many_times = fail_n_times_then_succeed(100)
    with patch("httpx.HTTPStatusError", MockException):
        with pytest.raises(_exceptions.InvalidResponseError):
            await fail_many_times()


async def test_retry_waits_long_enough(autojump_clock):
    fail_many_times = fail_n_times_then_succeed(100)
    with patch("httpx.HTTPStatusError", MockException):
        start_time = trio.current_time()
        with pytest.raises(_exceptions.InvalidResponseError):
            await fail_many_times()
        duration = trio.current_time() - start_time
    # Check duration of delay is roughly correct
    (dmax, dincrease) = (_download.MAX_DELAY, _download.INCREASE_FACTOR)
    min_total_delay = dmax / dincrease
    max_total_delay = (3 / 2) * dmax * dincrease / (dincrease - 1)
    assert min_total_delay < duration < max_total_delay


async def test_uses_retry_after_header(autojump_clock):
    # Arrange
    fail_once = fail_n_times_then_succeed(1, header=True)
    # Act
    start_time = trio.current_time()
    response = await fail_once()
    duration = trio.current_time() - start_time
    # Assert
    assert response.status_code == 200
    assert duration == RETRY_AFTER


async def test_retry_fails_with_other_status_codes(autojump_clock):
    fail_once = fail_n_times_then_succeed(1, fail_code=301)  # redirect

    with patch("httpx.HTTPStatusError", MockException):
        with pytest.raises(_exceptions.InvalidResponseError):
            await fail_once()
