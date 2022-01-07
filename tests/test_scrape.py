
import unittest
from unittest.mock import MagicMock, patch

from obscraper import post, scrape, grab

class TestGetPostsByURL(unittest.TestCase):
    def test_returns_valid_posts_for_valid_urls(self):
        urls = [
            'https://www.overcomingbias.com/2021/10/what-makes-stuff-rot.html',
            'https://www.overcomingbias.com/2014/07/limits-on-generality.html',
            'https://www.overcomingbias.com/2012/02/why-retire.html'
        ]
        posts = scrape.get_posts_by_url(urls)
        self.assertIsInstance(posts, list)
        self.assertTrue(len(posts), len(urls))
        for p in posts:
            self.assert_is_valid_post(p)

    def test_raises_exception_if_url_is_wrong_type(self):
        for urls in [
            ['https://www.overcomingbias.com/2007/10/a-rational-argu.html', None],
            [3514, 8293],
        ]:
            self.assertRaises(TypeError, scrape.get_posts_by_url, urls)

    def test_raises_exception_if_url_in_wrong_format(self):
        for urls in [
            ['Not a URL'],
            ['https://example.com/'],
            ['http://overcomingbias.com/'],
            ['https://www.overcomingbias.com/post.xml'],
            ['https://www.overcomingbias.com/page/20'],
            ['http://www.overcomingbias.com/archives'],
        ]:
            self.assertRaises(ValueError, scrape.get_posts_by_url, urls)

    def test_returns_none_for_invalid_urls(self):
        urls = [
            'https://www.overcomingbias.com/2007/10/a-rational-argu.html', # LessWrong URL
            'https://www.overcomingbias.com/2012/08/not-a-real-post.html', # Fake URL
            r'https://www.overcomingbias.com/2007/01/the-procrastinator%e2%80%99s-clock.html', # valid URL
            ]
        posts = scrape.get_posts_by_url(urls)
        self.assertIsNone(posts[0])
        self.assertIsNone(posts[1])
        self.assert_is_valid_post(posts[2])

    def assert_is_valid_post(self, p):
        self.assertIsInstance(p, post.Post)
        self.assertTrue(hasattr(p, 'words'))
        self.assertFalse(hasattr(p, 'votes'))
        self.assertFalse(hasattr(p, 'comments'))

class TestGetComments(unittest.TestCase):
    def test_returns_valid_comment_counts_for_valid_numbers(self):
        numbers = [27739, 33023, 26449]
        comments = scrape.get_comments(numbers)
        self.assertGreater(comments[numbers[0]], 100)
        self.assertGreater(comments[numbers[1]], 5)
        self.assertGreater(comments[numbers[2]], 30)
    
    def test_raises_type_error_if_numbers_are_wrong_type(self):
        for numbers in [
            [32451, [12345], 40591],
            ['Stringy', 23019, 49281],
        ]:
            self.assertRaises(TypeError, scrape.get_comments, numbers)

    def test_raises_value_error_if_numbers_out_of_range(self):
        for numbers in [
            [30219, 9999, 30194],
            [12345, 98752, 100000],
            [-31058, 20491]
        ]:
            self.assertRaises(ValueError, scrape.get_comments, numbers)

    def test_returns_none_for_invalid_numbers(self):
        numbers = [17209, 27056, 12345,]
        comments = scrape.get_comments(numbers)
        for c in [comments[numbers[0]], comments[numbers[2]]]:
            self.assertIsNone(c)
        self.assertIsInstance(comments[numbers[1]], int)
        self.assertGreater(comments[numbers[1]], 1)

class TestAttachEditDates(unittest.TestCase):
    def test_returns_post_with_date_attached_for_fake_posts_and_dates(self):
        # Expect more edit dates than posts
        edit_dates = {f'url {i+1}': f'edit date {i+1}' for i in range(10)}
        posts = [MagicMock(url=f'url {i+1}') for i in range(5)]
        with patch('obscraper.grab.grab_edit_dates', return_value=edit_dates) as mock_edit_dates:
            posts = scrape.attach_edit_dates(posts)
        mock_edit_dates.assert_called_once()
        for i, p in enumerate(posts):
            p.set_edit_date.assert_called_once_with(f'edit date {i+1}')

    def test_returns_none_for_invalid_post(self):
        # Posts which could not be found are returned as None
        edit_dates = {'fake url': 'fake edit date'}
        with patch('obscraper.grab.grab_edit_dates', return_value=edit_dates) as mock_edit_dates:
            invalid_post = scrape.attach_edit_dates([None])
        mock_edit_dates.assert_called_once()
        self.assertIsNone(invalid_post[0])

class TestRaiseExceptionIfNumberHasIncorrectFormat(unittest.TestCase):
    def test_no_exception_raised_if_number_has_correct_format(self):
        check_number = scrape.raise_exception_if_number_has_incorrect_format
        try:
            check_number(12345)
            check_number(54321)
            check_number(10000)
            check_number(99999)
        except ValueError:
            self.fail('ValueError raised')
        except TypeError:
            self.fail('TypeError raised')

    def test_type_error_raised_if_number_has_wrong_type(self):
        check_number = scrape.raise_exception_if_number_has_incorrect_format
        self.assertRaises(TypeError, check_number, 'Hello')
        self.assertRaises(TypeError, check_number, ['A', 'List'])
        self.assertRaises(TypeError, check_number, 32.591)
        self.assertRaises(TypeError, check_number, [12345])

    def test_value_error_raised_if_number_is_not_5_digits(self):
        check_number = scrape.raise_exception_if_number_has_incorrect_format
        self.assertRaises(ValueError, check_number, 1)
        self.assertRaises(ValueError, check_number, 9999)
        self.assertRaises(ValueError, check_number, 100000)
        self.assertRaises(ValueError, check_number, -12594)