from unittest.mock import MagicMock, NonCallableMock, patch
import unittest
from obscraper import download
import time

class Mock():
    pass

SUCCESS_RESPONSE = NonCallableMock(status_code=200)
RETRY_RESPONSE = NonCallableMock(status_code=429)

class TestHttpRequests(unittest.TestCase):
    
    @patch('requests.get')
    def test_http_get_passes_correct_arguments_when_no_header_is_provided(self, mock_request):
        mock_request.return_value = SUCCESS_RESPONSE
        url = 'https://example.com/'
        response = download.http_get_request(url)
        self.assertEqual(response.status_code, 200)
        mock_request.assert_called_once_with(url, headers={'user-agent': 'Mozilla/5.0'})
    
    @patch('requests.get')
    def test_http_get_passes_correct_arguments_when_user_agent_is_provided(self, mock_request):
        mock_request.return_value = SUCCESS_RESPONSE
        url = 'https://example.com/'
        response = download.http_get_request(url, headers={'user-agent': 'Modified User Agent'})
        self.assertEqual(response.status_code, 200)
        mock_request.assert_called_once_with(url, headers={'user-agent': 'Modified User Agent'})

    @patch('requests.get')
    def test_http_get_passes_correct_arguments_when_extra_headers_are_provided(self, mock_request):
        mock_request.return_value = SUCCESS_RESPONSE
        url = 'https://example.com/'
        response = download.http_get_request(url, headers={'extra-header': 'Extra Info'})
        self.assertEqual(response.status_code, 200)
        mock_request.assert_called_once_with(url, headers={'user-agent': 'Mozilla/5.0', 'extra-header': 'Extra Info'})
    
    @patch('requests.post')
    def test_http_post_passes_correct_arguments_when_params_are_provided(self, mock_request):
        mock_request.return_value = SUCCESS_RESPONSE
        url = 'https://example.com/'
        params = {
            'param 1': 'First Parameter', 
            'param 2': 'Second Parameter'
        }
        response = download.http_post_request(url, params=params)
        self.assertEqual(response.status_code, 200)
        mock_request.assert_called_once_with(url, headers={'user-agent': 'Mozilla/5.0'}, params=params)

class TestRetryRequest(unittest.TestCase):

    def fail_n_times_then_succeed(self, n):
        """Function which fails n times before succeeding."""
        mock_method = MagicMock(side_effect = [RETRY_RESPONSE] * n + [SUCCESS_RESPONSE])
        @download.retry_request(0.2)
        def mock_responder():
            return mock_method()
        return mock_responder

    def test_retry_can_succeed_first_time(self):
        fail_zero_times = self.fail_n_times_then_succeed(0)
        response = fail_zero_times()
        self.assertEqual(response.status_code, 200)

    @unittest.skipIf(download.MAX_TRIES < 4, 'Maximum tries too small')
    def test_retry_succeeds_after_a_few_unsuccessful_tries(self):
        fail_three_times = self.fail_n_times_then_succeed(3)
        response = fail_three_times()
        self.assertEqual(response.status_code, 200)

    def test_retry_gives_up_after_max_tries(self):
        fail_many_times = self.fail_n_times_then_succeed(100)
        response = fail_many_times()
        self.assertEqual(response.status_code, 429)

    def test_retry_waits_long_enough(self):
        fail_one_time = self.fail_n_times_then_succeed(1)
        start_time = time.time()
        response = fail_one_time()
        duration = time.time() - start_time
        self.assertEqual(response.status_code, 200)
        # Check duration of delay is roughly correct
        self.assertTrue(duration > 0.8 * download.RETRY_DELAY)