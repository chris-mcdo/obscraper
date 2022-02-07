from unittest.mock import AsyncMock, MagicMock, NonCallableMock
import unittest
from obscraper import _download
import time

SUCCESS_RESPONSE = NonCallableMock(status_code=200)
RETRY_RESPONSE = NonCallableMock(status_code=429)
RETRY_RESPONSE_WITH_HEADER = NonCallableMock(
    status_code=429, headers=MagicMock(headers={'Retry-After': '2'}))

class TestRetryRequest(unittest.IsolatedAsyncioTestCase):

    def fail_n_times_then_succeed(self, n, header=False):
        """Function which fails n times before succeeding."""
        retry = RETRY_RESPONSE_WITH_HEADER if header else RETRY_RESPONSE
        mock_method = AsyncMock(
            side_effect=[retry] * n + [SUCCESS_RESPONSE])

        @_download.async_retry_request
        async def mock_responder():
            response = await mock_method()
            return response
        return mock_responder

    async def test_retry_can_succeed_first_time(self):
        fail_zero_times = self.fail_n_times_then_succeed(0)
        response = await fail_zero_times()
        self.assertEqual(response.status_code, 200)

    async def test_retry_succeeds_after_a_few_unsuccessful_tries(self):
        fail_two_times = self.fail_n_times_then_succeed(2)
        response = await fail_two_times()
        self.assertEqual(response.status_code, 200)

    async def test_retry_gives_up_after_max_tries(self):
        fail_many_times = self.fail_n_times_then_succeed(100)
        response = await fail_many_times()
        self.assertEqual(response.status_code, 429)

    async def test_retry_waits_long_enough(self):
        fail_many_times = self.fail_n_times_then_succeed(100)
        start_time = time.time()
        response = await fail_many_times()
        duration = time.time() - start_time
        self.assertEqual(response.status_code, 429)
        # Check duration of delay is roughly correct
        (dmax, dincrease) = (_download.MAX_DELAY, _download.INCREASE_FACTOR)
        self.assertTrue(duration > dmax / dincrease)
        max_total_delay = (3 / 2) * dmax * dincrease / (dincrease - 1)
        # ^ do the math
        self.assertTrue(duration < max_total_delay)

    async def test_uses_retry_after_header(self):
        # Arrange
        fail_once = self.fail_n_times_then_succeed(1, header=True)
        retry_after = int(RETRY_RESPONSE_WITH_HEADER.headers['Retry-After'])
        # Act
        start_time = time.time()
        response = await fail_once()
        duration = time.time() - start_time
        # Assert
        self.assertEqual(response.status_code, 200)
        self.assertGreater(duration, retry_after)
        self.assertLess(duration, retry_after * 1.5)
