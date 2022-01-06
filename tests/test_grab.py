
import datetime
import unittest
from unittest.mock import MagicMock, patch
from obscraper import extract_page, grab, exceptions, post

TEST_POST_NUMBER = 27739
TEST_POST_MIN_VOTES = 150
TEST_POST_MIN_COMMENTS = 100

class TestGrabPostByURL(unittest.TestCase):

    def test_grab_post_fails_with_lesswrong_post_url(self):
        self.assertRaises(ValueError, grab.grab_post_by_url, 'https://www.overcomingbias.com/2007/10/a-rational-argu.html')

    def test_grab_post_fails_with_fake_post_url(self):
        self.assertRaises(exceptions.InvalidResponseError, grab.grab_post_by_url, 'http://www.overcomingbias.com/2020/01/not-a-real-post.html')

    def test_grab_post_fails_with_bad_url(self):
        grab_post = grab.grab_post_by_url
        self.assertRaises(ValueError, grab_post, 'https://example.com/')
        self.assertRaises(ValueError, grab_post, 'https://overcomingbias.com/')
        self.assertRaises(ValueError, grab_post, 'https://overcomingbias.com/page/1')
        self.assertRaises(ValueError, grab_post, 'https://overcomingbias.com/not-a-real-page.html')
        self.assertRaises(ValueError, grab_post, 'https://overcomingbias.com/2021/05/page/2')

    def test_grab_post_works_with_real_urls(self):
        self.grab_fake_post('http://www.overcomingbias.com/?p=33023')
        self.grab_fake_post('https://www.overcomingbias.com/2021/12/innovation-liability-nightmare.html')

    @patch('obscraper.extract_page.is_ob_site_html')
    @patch('obscraper.extract_page.is_single_ob_post_html')
    @patch('obscraper.post.create_post')
    @patch('obscraper.download.grab_html_soup')
    def grab_fake_post(self, url, mock_grab_html, mock_create_post, mock_is_ob_post, mock_is_from_ob_site):
        # Arrange
        mock_is_from_ob_site.return_value = True
        mock_is_ob_post.return_value = True
        mock_grab_html.return_value = 'Mock html'
        mock_create_post.return_value = 'Mock post'
        # Act
        grab.grab_post_by_url(url)
        # Assert
        mock_grab_html.assert_called_once_with(url)
        mock_is_ob_post.assert_called_once_with('Mock html')
        mock_is_from_ob_site.assert_called_once_with('Mock html')
        mock_create_post.assert_called_once_with('Mock html')

class TestGrabPage(unittest.TestCase):
    def test_page_0_raises_value_error(self):
        self.assertRaises(ValueError, grab.grab_page, page=0)

    def test_page_10000_raises_invalid_response_error(self):
        self.assertRaises(exceptions.InvalidResponseError, grab.grab_page, page=10000)

    def test_page_1_returns_valid_ob_page(self):
        page_1 = grab.grab_page(1)
        self.assertTrue(extract_page.is_ob_page_html(page_1))

    def test_page_300_return_valid_ob_page(self):
        page_300 = grab.grab_page(300)
        self.assertTrue(extract_page.is_ob_page_html(page_300))

class TestGrabAllPostsOnPageAndGrabPublishDates(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.addClassCleanup(patch.stopall)
        cls.test_page = 1
        patcher = patch('obscraper.grab.grab_page', return_value = grab.grab_page(cls.test_page))
        cls.mock_grab_page = patcher.start()
    
    def test_normal_page_is_grabbed_correctly(self):
        post_list = grab.grab_all_posts_on_page(self.test_page)
        # Is it a list of posts?
        self.assertIsInstance(post_list, list)
        self.assertEqual(len(post_list), 10)
        for p in post_list:
            self.assertIsInstance(p, post.Post)
            self.assertTrue(hasattr(p, 'words'))

    @patch('obscraper.extract_page.has_post_moved')
    def test_page_with_moved_but_not_truncated_post_is_grabbed_correctly(self, mock_has_post_moved):
        mock_has_post_moved.side_effect = [False] * 9 + [True]
        post_list = grab.grab_all_posts_on_page(self.test_page)
        self.assertIsInstance(post_list, list)
        self.assertEqual(len(post_list), 10)
        for p in post_list:
            self.assertIsInstance(p, post.Post)
            self.assertTrue(hasattr(p, 'words'))

    def test_page_with_moved_and_truncated_post_is_grabbed_correctly(self):
        # TODO
        # This gets difficult when patching is involved
        pass

    def test_grab_publish_date_works_as_expected(self):
        # Arrange
        utc = datetime.timezone.utc
        # Act
        dates = grab.grab_publish_dates(self.test_page)
        # Assert
        # Returns 10 items
        self.assertEqual(len(dates), 10)
        for d in dates:
            # Type is datetime.datetime
            self.assertIsInstance(d, datetime.datetime)
            # Dates are between 2000 and now
            self.assertGreater(d, datetime.datetime(2000, 1, 1, tzinfo=utc))
            self.assertLess(d, datetime.datetime.now(utc))


class TestGrabComments(unittest.TestCase):
    @patch('obscraper.download.http_post_request')
    def test_grab_comments_gives_correct_arguments_to_http_post_request(self, mock_post_request):
        # Arrange
        # Return invalid response
        mock_post_request.return_value.text = r'displayCount({"text":[],"counts":[]});'
        params = {'1': grab.disqus_identifier(TEST_POST_NUMBER)}
        # Act
        self.assertRaises(exceptions.InvalidResponseError, grab.grab_comments, TEST_POST_NUMBER)
        mock_post_request.assert_called_once_with(grab.DISQUS_URL, params=params)
    
    def test_grab_comments_returns_more_than_min_comments_for_some_post(self):
        result = grab.grab_comments(TEST_POST_NUMBER)
        self.assertIsInstance(result, int)
        self.assertGreater(result, TEST_POST_MIN_COMMENTS)

    def test_grab_comments_raises_exception_with_invalid_number(self):
        self.assertRaises(exceptions.InvalidResponseError, grab.grab_comments, 123)

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
        self.assertTrue(extract_page.is_ob_post_url(urls[0]))
        self.assertTrue(extract_page.is_ob_post_url(urls[-10]))

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
