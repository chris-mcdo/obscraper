
import datetime
import unittest
from unittest.mock import MagicMock, patch
from obscraper import extract_post, grab, exceptions, post
from test_extract import TEST_DISQUS_IDS

TEST_POST_NUMBER = 27739
TEST_POST_MIN_VOTES = 150
TEST_POST_MIN_COMMENTS = 100

class TestGrabPostByURL(unittest.TestCase):

    def test_grab_post_fails_with_lesswrong_post_url(self):
        self.assertRaises(exceptions.InvalidResponseError, grab.grab_post_by_url, 'https://www.overcomingbias.com/2007/10/a-rational-argu.html')

    def test_grab_post_fails_with_fake_post_url(self):
        self.assertRaises(exceptions.InvalidResponseError, grab.grab_post_by_url, 'http://www.overcomingbias.com/2020/01/not-a-real-post.html')

    def test_grab_post_works_with_number_url(self):
        p = grab.grab_post_by_url(f'http://www.overcomingbias.com/?p={TEST_POST_NUMBER}')
        self.assertIsInstance(p, post.Post)
        self.assertEqual(p.number, TEST_POST_NUMBER)
        self.assertGreater(p.word_count, 10)

    def test_grab_post_works_with_string_url(self):
        test_url = 'https://www.overcomingbias.com/2021/12/innovation-liability-nightmare.html'
        p = grab.grab_post_by_url(test_url)
        self.assertIsInstance(p, post.Post)
        self.assertEqual(p.url, test_url)
        self.assertGreater(p.word_count, 10)

class TestGrabComments(unittest.TestCase):
    def test_returns_valid_count_for_example_post_numbers(self):
        for disqus_id in TEST_DISQUS_IDS.values():
            result = grab.grab_comments(disqus_id)
            self.assertIsInstance(result, int)
            self.assertGreater(result, 2)

    def test_grab_comments_raises_exception_with_invalid_number(self):
        bad_id = '12345 https://www.overcomingbias.com/?p=12345'
        self.assertRaises(exceptions.InvalidResponseError, grab.grab_comments, bad_id)

class TestGrabEditDates(unittest.TestCase):
    def test_grab_edit_dates_returns_expected_result(self):
        # Arrange
        utc = datetime.timezone.utc
        # Act
        edit_dates = grab.grab_edit_dates()
        urls = list(edit_dates.keys())
        dates = list(edit_dates.values())
        # Assert
        # Check result is dict
        self.assertIsInstance(edit_dates, dict)
        self.assertIsInstance(dates[0], datetime.datetime)
        # Check elements are dates between 2000 and tomorrow
        self.assertGreater(dates[-1], datetime.datetime(2000, 1, 1, tzinfo=utc))
        self.assertLess(dates[0], datetime.datetime.now(utc))
        # Test first and last elements is valid post urls
        self.assertTrue(extract_post.is_ob_post_url(urls[0]))
        self.assertTrue(extract_post.is_ob_post_url(urls[-10]))

class TestGrabVotes(unittest.TestCase):

    @patch('obscraper.download.http_post_request')
    @patch('obscraper.grab.vote_auth_code')
    def test_grab_votes_gives_correct_arguments_to_http_post_request(self, mock_auth_code, mock_post_request):
        # Arrange
        # Strip decorator from grab_votes
        grab_votes_unwrapped = grab.grab_votes.__wrapped__
        mock_auth_code.return_value = 'notarealcode'
        mock_post_request.return_value.text = '-1'
        headers = {'x-requested-with': 'XMLHttpRequest'}
        params = {
            '_ajax_nonce': mock_auth_code.return_value,
            'vote_type': 'cache',
            'vote_domain': 'a',
            'votes': f'atr.{TEST_POST_NUMBER}'
            }
        # Act
        self.assertRaises(exceptions.InvalidAuthCodeError, grab_votes_unwrapped, TEST_POST_NUMBER)
        mock_post_request.assert_called_once_with(grab.GDSR_URL, params=params, headers=headers)

    def test_grab_votes_returns_more_than_min_votes_for_some_post(self):
        result = grab.grab_votes(TEST_POST_NUMBER)
        self.assertIsInstance(result, int)
        self.assertGreater(result, TEST_POST_MIN_VOTES)
    
    @patch('obscraper.grab.vote_auth_code')
    def test_grab_votes_raises_exception_with_invalid_vote_auth_code(self, mock_auth_code):
        grab_votes_unwrapped = grab.grab_votes.__wrapped__
        mock_auth_code.return_value = 'notarealcode'
        self.assertRaises(exceptions.InvalidAuthCodeError, grab_votes_unwrapped, TEST_POST_NUMBER)

class TestCacheAuth(unittest.TestCase):
    def raise_invalid_auth_code_error_n_times_then_succeed(self, n):
        """Function which raises an InvalidAuthCodeError n times before succeeding."""
        mock_function = MagicMock(side_effect = [exceptions.InvalidAuthCodeError] * n + ['Success!'])
        @grab.cache_auth
        def mock_responder(arg_without_default, arg_with_default='Second Arg'):
            return mock_function(arg_without_default, arg_with_default)
        return (mock_responder, mock_function)

    @patch('obscraper.grab.vote_auth_code')
    def test_cache_auth_works_if_method_succeeds_first_time(self, mock_auth_code):
        # Arrange
        (succeed_first_time, mock_function) = self.raise_invalid_auth_code_error_n_times_then_succeed(0)
        # Act
        result = succeed_first_time('First Arg')
        # Assert
        self.assertEqual(result, 'Success!')
        mock_auth_code.cache_clear.assert_not_called()
        mock_function.assert_called_once_with('First Arg', 'Second Arg')
    
    @patch('obscraper.grab.vote_auth_code')
    def test_cache_auth_works_if_method_gives_invalid_auth_code_error_then_succeeds(self, mock_auth_code):
        # Arrange
        (succeed_second_time, mock_function) = self.raise_invalid_auth_code_error_n_times_then_succeed(1)
        # Act
        result = succeed_second_time('First Arg', 'Second Arg')
        self.assertEqual(result, 'Success!')
        mock_auth_code.cache_clear.assert_called_once()
        self.assertEqual(mock_function.call_count, 2)
        mock_function.assert_called_with('First Arg', 'Second Arg')

    @patch('obscraper.grab.vote_auth_code')
    def test_cache_auth_raises_exception_if_method_raises_exception_twice(self, mock_auth_code):
        (fail_twice, mock_function) = self.raise_invalid_auth_code_error_n_times_then_succeed(2)
        self.assertRaises(exceptions.InvalidAuthCodeError, fail_twice, 'First Arg', arg_with_default='Second Arg')
        mock_auth_code.cache_clear.assert_called_once()
        self.assertEqual(mock_function.call_count, 2)
        mock_function.assert_called_with('First Arg', 'Second Arg')

class TestVoteAuthCode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vote_auth_code = grab.vote_auth_code()
    
    def test_grabbed_vote_auth_code_is_in_correct_format(self):
        self.assertRegex(self.vote_auth_code, r'^[a-z0-9]{10}$')

    def test_vote_auth_code_works_for_test_post(self):
        with patch('obscraper.grab.vote_auth_code', return_value=self.vote_auth_code):
            votes = grab.grab_votes(TEST_POST_NUMBER)
            self.assertIsInstance(votes, int)
            self.assertGreater(votes, TEST_POST_MIN_VOTES)
