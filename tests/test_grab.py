import unittest
from unittest.mock import MagicMock, patch

import datetime
import time
import cachetools.func

from obscraper import _exceptions, _extract_post, _grab, _post, _utils, _download
from test_extract import TEST_POST_NUMBERS, TEST_DISQUS_IDS


TEST_POST_NUMBER = 27739
TEST_POST_MIN_VOTES = 150
TEST_POST_MIN_COMMENTS = 100


class TestGrabPostByURL(unittest.TestCase):

    def test_grab_post_fails_with_lesswrong_post_url(self):
        self.assertRaises(_exceptions.InvalidResponseError, _grab.grab_post_by_url,
                          'https://www.overcomingbias.com/2007/10/a-rational-argu.html')

    def test_grab_post_fails_with_fake_post_url(self):
        self.assertRaises(_exceptions.InvalidResponseError, _grab.grab_post_by_url,
                          'http://www.overcomingbias.com/2020/01/not-a-real-post.html')

    def test_grab_post_works_with_number_url(self):
        p = _grab.grab_post_by_url(
            f'http://www.overcomingbias.com/?p={TEST_POST_NUMBER}')
        self.assertIsInstance(p, _post.Post)
        self.assertEqual(p.number, TEST_POST_NUMBER)
        self.assertGreater(p.word_count, 10)

    def test_grab_post_works_with_string_url(self):
        test_url = 'https://www.overcomingbias.com/2021/12/innovation-liability-nightmare.html'
        p = _grab.grab_post_by_url(test_url)
        self.assertIsInstance(p, _post.Post)
        self.assertEqual(p.url, test_url)
        self.assertGreater(p.word_count, 10)


class TestGrabComments(unittest.TestCase):
    def test_returns_valid_count_for_example_post_numbers(self):
        for disqus_id in TEST_DISQUS_IDS.values():
            result = _grab.grab_comments(disqus_id)
            self.assertIsInstance(result, int)
            self.assertGreater(result, 2)

    def test_grab_comments_raises_exception_with_invalid_number(self):
        bad_id = '12345 https://www.overcomingbias.com/?p=12345'
        self.assertRaises(_exceptions.InvalidResponseError,
                          _grab.grab_comments, bad_id)


class TestGrabEditDates(unittest.TestCase):
    def test_grab_edit_dates_returns_expected_result(self):
        # Arrange
        utc = datetime.timezone.utc
        # Act
        edit_dates = _grab.grab_edit_dates()
        urls = list(edit_dates.keys())
        dates = list(edit_dates.values())
        # Assert
        # Check result is dict
        self.assertIsInstance(edit_dates, dict)
        self.assertIsInstance(dates[0], datetime.datetime)
        # Check elements are dates between 2000 and tomorrow
        self.assertGreater(
            dates[-1], datetime.datetime(2000, 1, 1, tzinfo=utc))
        self.assertLess(dates[0], datetime.datetime.now(utc))
        # Test first and last elements is valid post urls
        self.assertTrue(_extract_post.is_valid_post_url(urls[0]))
        self.assertTrue(_extract_post.is_valid_post_url(urls[-10]))


class TestGrabVotes(unittest.TestCase):

    @patch('obscraper._download.http_post_request')
    @patch('obscraper._grab.vote_auth_code')
    def test_grab_votes_gives_correct_arguments_to_http_post_request(self, mock_auth_code, mock_post_request):
        # Arrange
        # Strip decorator from grab_votes
        grab_votes_unwrapped = _grab.grab_votes.__wrapped__.__wrapped__
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
        self.assertRaises(_exceptions.InvalidAuthCodeError,
                          grab_votes_unwrapped, TEST_POST_NUMBER)
        mock_post_request.assert_called_once_with(
            _grab.GDSR_URL, params=params, headers=headers)

    def test_grab_votes_returns_more_than_min_votes_for_some_post(self):
        result = _grab.grab_votes(TEST_POST_NUMBER)
        self.assertIsInstance(result, int)
        self.assertGreater(result, TEST_POST_MIN_VOTES)

    @patch('obscraper._grab.vote_auth_code')
    def test_grab_votes_raises_exception_with_invalid_vote_auth_code(self, mock_auth_code):
        grab_votes_unwrapped = _grab.grab_votes.__wrapped__
        mock_auth_code.return_value = 'notarealcode'
        self.assertRaises(_exceptions.InvalidAuthCodeError,
                          grab_votes_unwrapped, TEST_POST_NUMBER)


class TestCacheAuth(unittest.TestCase):
    def raise_invalid_auth_code_error_n_times_then_succeed(self, n):
        """Function which raises an InvalidAuthCodeError n times before succeeding."""
        mock_function = MagicMock(
            side_effect=[_exceptions.InvalidAuthCodeError] * n + ['Success!'])

        @_grab._auth_cache
        def mock_responder(arg_without_default, arg_with_default='Second Arg'):
            return mock_function(arg_without_default, arg_with_default)
        return (mock_responder, mock_function)

    @patch('obscraper._grab.vote_auth_code')
    def test_cache_auth_works_if_method_succeeds_first_time(self, mock_auth_code):
        # Arrange
        (succeed_first_time,
         mock_function) = self.raise_invalid_auth_code_error_n_times_then_succeed(0)
        # Act
        result = succeed_first_time('First Arg')
        # Assert
        self.assertEqual(result, 'Success!')
        mock_auth_code.cache_clear.assert_not_called()
        mock_function.assert_called_once_with('First Arg', 'Second Arg')

    @patch('obscraper._grab.vote_auth_code')
    def test_cache_auth_works_if_method_gives_invalid_auth_code_error_then_succeeds(self, mock_auth_code):
        # Arrange
        (succeed_second_time,
         mock_function) = self.raise_invalid_auth_code_error_n_times_then_succeed(1)
        # Act
        result = succeed_second_time('First Arg', 'Second Arg')
        self.assertEqual(result, 'Success!')
        mock_auth_code.cache_clear.assert_called_once()
        self.assertEqual(mock_function.call_count, 2)
        mock_function.assert_called_with('First Arg', 'Second Arg')

    @patch('obscraper._grab.vote_auth_code')
    def test_cache_auth_raises_exception_if_method_raises_exception_twice(self, mock_auth_code):
        (fail_twice, mock_function) = self.raise_invalid_auth_code_error_n_times_then_succeed(2)
        self.assertRaises(_exceptions.InvalidAuthCodeError,
                          fail_twice, 'First Arg', arg_with_default='Second Arg')
        mock_auth_code.cache_clear.assert_called_once()
        self.assertEqual(mock_function.call_count, 2)
        mock_function.assert_called_with('First Arg', 'Second Arg')


class TestVoteAuthCode(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vote_auth_code = _grab.vote_auth_code()

    def test_grabbed_vote_auth_code_is_in_correct_format(self):
        self.assertRegex(self.vote_auth_code, r'^[a-z0-9]{10}$')

    def test_vote_auth_code_works_for_test_post(self):
        with patch('obscraper._grab.vote_auth_code', return_value=self.vote_auth_code):
            votes = _grab.grab_votes(TEST_POST_NUMBER)
            self.assertIsInstance(votes, int)
            self.assertGreater(votes, TEST_POST_MIN_VOTES)


class TestCaching(unittest.TestCase):
    @patch('obscraper._download.http_post_request')
    def test_cached_values_can_be_cleared(self, mock_http_post):
        mock_http_post.return_value = MagicMock(
            text=r'DISQUSWIDGETS.displayCount({"counts":[{"comments":5}]});')
        self.assertEqual(_grab.grab_comments('Fake Disqus ID'), 5)

        mock_http_post.return_value = MagicMock(
            text=r'DISQUSWIDGETS.displayCount({"counts":[{"comments":10}]});')
        mock_http_post.assert_called_once()
        self.assertEqual(_grab.grab_comments('Fake Disqus ID'), 5)

        _grab.grab_comments.cache_clear()
        self.assertEqual(_grab.grab_comments('Fake Disqus ID'), 10)

    def test_cache_times_out_as_expected(self):
        # Arrange
        mock_to_return = MagicMock()

        @cachetools.func.ttl_cache(maxsize=10, ttl=1)
        def cached_mock():
            return mock_to_return()

        # Act and assert
        mock_to_return.return_value = 'Initial Mock'
        self.assertEqual(cached_mock(), 'Initial Mock')
        mock_to_return.assert_called_once()

        mock_to_return.return_value = 'New Mock'
        self.assertEqual(cached_mock(), 'Initial Mock')
        mock_to_return.assert_called_once()

        time.sleep(1)
        self.assertEqual(cached_mock(), 'New Mock')

    def test_cache_runs_out_of_size_as_expected(self):
        # Arrange
        @cachetools.func.ttl_cache(maxsize=2, ttl=100)
        def cached_speech(says):
            return f'Say {says}'

        # Act and assert
        self.assertEqual(cached_speech('hi'), 'Say hi')
        self.assertEqual(cached_speech('bye'), 'Say bye')
        self.assertEqual(cached_speech('yes'), 'Say yes')
        self.assertEqual(cached_speech('hi'), 'Say hi')
        self.assertEqual(cached_speech('yes'), 'Say yes')

        self.assertEqual(cached_speech.cache_info().misses, 4)
        self.assertEqual(cached_speech.cache_info().hits, 1)


class TestCreatePost(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.post_htmls = {
            number:
            _download.grab_html_soup(
                f'https://www.overcomingbias.com/?p={number}')
            for number in TEST_POST_NUMBERS
        }

    def test_returns_valid_posts_for_valid_htmls(self):
        for html in self.post_htmls.values():
            p = _grab.create_post(html, votes=False, comments=False)
            self.assert_is_valid_post(p, votes=False, comments=False)

    def test_returns_valid_posts_for_valid_htmls_with_votes(self):
        for html in self.post_htmls.values():
            p = _grab.create_post(html, votes=True, comments=False)
            self.assert_is_valid_post(p, votes=True, comments=False)

    def test_returns_valid_posts_for_valid_htmls_with_comments(self):
        for html in self.post_htmls.values():
            p = _grab.create_post(html, votes=False, comments=True)
            self.assert_is_valid_post(p, votes=False, comments=True)

    def assert_is_valid_post(self, test_post, votes, comments):
        self.assert_post_has_standard_attributes(test_post)
        self.assert_post_standard_attributes_have_correct_types(test_post)
        self.assert_post_standard_attributes_have_valid_values(test_post)
        if votes:
            self.assertIsInstance(test_post.votes, int)
            self.assertGreaterEqual(test_post.votes, 0)
        else:
            self.assertIsNone(test_post.votes)
        if comments:
            self.assertIsInstance(test_post.comments, int)
            self.assertGreaterEqual(test_post.comments, 0)
        else:
            self.assertIsNone(test_post.comments)

    def assert_post_has_standard_attributes(self, test_post):
        self.assertIsInstance(test_post, _post.Post)
        for attr in [
            'url', 'name', 'title', 'author', 'publish_date', 'number', 'tags', 'categories',
            'page_type', 'page_status', 'page_format', 'text_html', 'word_count', 'internal_links', 'external_links', 'disqus_id',
        ]:
            self.assertTrue(hasattr(test_post, attr))

    def assert_post_standard_attributes_have_correct_types(self, test_post):
        # str
        for attr in ['url', 'name', 'title', 'author', 'page_type', 'page_status', 'page_format', 'text_html', 'disqus_id', ]:
            self.assertIsInstance(getattr(test_post, attr), str)
        # datetime.datetime
        self.assertIsInstance(test_post.publish_date, datetime.datetime)
        # int
        self.assertIsInstance(test_post.number, int)
        self.assertIsInstance(test_post.word_count, int)
        # list
        self.assertIsInstance(test_post.tags, list)
        self.assertIsInstance(test_post.categories, list)
        # list elements
        [self.assertIsInstance(tag, str) for tag in test_post.tags]
        [self.assertIsInstance(cat, str) for cat in test_post.categories]
        # dict
        self.assertIsInstance(test_post.internal_links, dict)
        self.assertIsInstance(test_post.external_links, dict)
        # dict elements
        [self.assertIsInstance(url, str)
         for url in test_post.internal_links.keys()]
        [self.assertIsInstance(number, int)
         for number in test_post.internal_links.values()]
        [self.assertIsInstance(url, str)
         for url in test_post.external_links.keys()]
        [self.assertIsInstance(number, int)
         for number in test_post.external_links.values()]

    def assert_post_standard_attributes_have_valid_values(self, test_post):
        # URL and title
        self.assertTrue(_extract_post.is_valid_post_long_url(test_post.url))
        self.assertRegex(test_post.name, r'^[a-z0-9-_%]+$')
        # Metadata
        self.assertTrue(9999 < test_post.number < 100000)
        self.assertEqual(test_post.page_type, 'post')
        self.assertEqual(test_post.page_status, 'publish')
        self.assertEqual(test_post.page_format, 'standard')
        # Tags and categories
        [self.assertRegex(tag, r'^[a-z0-9-]+$') for tag in test_post.tags]
        [self.assertRegex(cat, r'^[a-z0-9-]+$')
         for cat in test_post.categories]
        # Title, author, date
        self.assertNotEqual(test_post.title, '')
        self.assertRegex(test_post.author, r'^[A-Za-z0-9\. ]+$')
        self.assertTrue(_utils.is_aware_datetime(test_post.publish_date))
        # Word count and links
        self.assertNotEqual(test_post.plaintext, '')
        self.assertGreater(test_post.word_count, 5)
        [self.assertTrue(_extract_post.is_valid_post_url(url))
         for url in test_post.internal_links.keys()]
        [self.assertGreaterEqual(number, 1)
         for number in test_post.internal_links.values()]
        [self.assertFalse(_extract_post.is_valid_post_url(url))
         for url in test_post.external_links.keys()]
        [self.assertGreaterEqual(number, 1)
         for number in test_post.external_links.values()]
        # Disqus ID string
        self.assertTrue(_extract_post.is_valid_disqus_id(test_post.disqus_id))
