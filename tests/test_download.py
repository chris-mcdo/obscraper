from unittest.mock import MagicMock, NonCallableMock, patch
import unittest
from obscraper import _download
import time
import math

SUCCESS_RESPONSE = NonCallableMock(status_code=200)
RETRY_RESPONSE = NonCallableMock(status_code=429)


class TestHttpRequests(unittest.TestCase):

    @patch('requests.get')
    def test_http_get_passes_correct_arguments_when_no_header_is_provided(self, mock_request):
        mock_request.return_value = SUCCESS_RESPONSE
        url = 'https://example.com/'
        response = _download.http_get_request(url)
        self.assertEqual(response.status_code, 200)
        mock_request.assert_called_once_with(
            url, headers={'user-agent': 'Mozilla/5.0'})

    @patch('requests.get')
    def test_http_get_passes_correct_arguments_when_user_agent_is_provided(self, mock_request):
        mock_request.return_value = SUCCESS_RESPONSE
        url = 'https://example.com/'
        response = _download.http_get_request(
            url, headers={'user-agent': 'Modified User Agent'})
        self.assertEqual(response.status_code, 200)
        mock_request.assert_called_once_with(
            url, headers={'user-agent': 'Modified User Agent'})

    @patch('requests.get')
    def test_http_get_passes_correct_arguments_when_extra_headers_are_provided(self, mock_request):
        mock_request.return_value = SUCCESS_RESPONSE
        url = 'https://example.com/'
        response = _download.http_get_request(
            url, headers={'extra-header': 'Extra Info'})
        self.assertEqual(response.status_code, 200)
        mock_request.assert_called_once_with(
            url, headers={'user-agent': 'Mozilla/5.0', 'extra-header': 'Extra Info'})

    @patch('requests.post')
    def test_http_post_passes_correct_arguments_when_params_are_provided(self, mock_request):
        mock_request.return_value = SUCCESS_RESPONSE
        url = 'https://example.com/'
        params = {
            'param 1': 'First Parameter',
            'param 2': 'Second Parameter'
        }
        response = _download.http_post_request(url, params=params)
        self.assertEqual(response.status_code, 200)
        mock_request.assert_called_once_with(
            url, headers={'user-agent': 'Mozilla/5.0'}, params=params)


class TestRetryRequest(unittest.TestCase):

    def fail_n_times_then_succeed(self, n):
        """Function which fails n times before succeeding."""
        mock_method = MagicMock(
            side_effect=[RETRY_RESPONSE] * n + [SUCCESS_RESPONSE])

        @_download.retry_request
        def mock_responder():
            return mock_method()
        return mock_responder

    def test_retry_can_succeed_first_time(self):
        fail_zero_times = self.fail_n_times_then_succeed(0)
        response = fail_zero_times()
        self.assertEqual(response.status_code, 200)

    def test_retry_succeeds_after_a_few_unsuccessful_tries(self):
        fail_two_times = self.fail_n_times_then_succeed(2)
        response = fail_two_times()
        self.assertEqual(response.status_code, 200)

    def test_retry_gives_up_after_max_tries(self):
        fail_many_times = self.fail_n_times_then_succeed(100)
        response = fail_many_times()
        self.assertEqual(response.status_code, 429)

    def test_retry_waits_long_enough(self):
        fail_many_times = self.fail_n_times_then_succeed(100)
        start_time = time.time()
        response = fail_many_times()
        duration = time.time() - start_time
        self.assertEqual(response.status_code, 429)
        # Check duration of delay is roughly correct
        self.assertTrue(duration > 0.5 * _download.MAX_DELAY)
        (dmax, dincrease) = (_download.MAX_DELAY, _download.INCREASE_FACTOR)
        max_total_delay = (3 / 2) * dmax * dincrease / \
            (dincrease - 1)  # do the math
        self.assertTrue(duration < max_total_delay)
