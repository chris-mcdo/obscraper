
import unittest
from unittest.mock import MagicMock, patch

import datetime

from obscraper import exceptions, post, scrape, grab

class TestGetPostsByURL(unittest.TestCase):
    def test_works_for_3_urls(self):
        urls = [
            'https://www.overcomingbias.com/2021/10/what-makes-stuff-rot.html',
            'https://www.overcomingbias.com/2014/07/limits-on-generality.html',
            'https://www.overcomingbias.com/2012/02/why-retire.html'
        ]
        posts = scrape.get_posts_by_url(urls)
        self.assertIsInstance(posts, list)
        self.assertTrue(len(posts), len(urls))
        for p in posts:
            self.assertIsInstance(p, post.Post)
            self.assertTrue(hasattr(p, 'words'))
            self.assertFalse(hasattr(p, 'votes'))
            self.assertFalse(hasattr(p, 'comments'))

    def test_raises_exception_for_lesswrong_url(self):
        url = ['https://www.overcomingbias.com/2007/10/a-rational-argu.html']
        self.assertRaises(exceptions.InvalidResponseError, scrape.get_posts_by_url, url)

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

class TestGetStartPage(unittest.TestCase):
    # TODO
    # Partially tested in TestGetPostsByDate
    pass

class TestAttachEditDates(unittest.TestCase):
    def test_works_as_expected_for_fake_posts_and_dates(self):
        # Expect more edit dates than posts
        edit_dates = {f'url {i+1}': f'edit date {i+1}' for i in range(10)}
        posts = [MagicMock(url=f'url {i+1}') for i in range(5)]
        with patch('obscraper.grab.grab_edit_dates', return_value=edit_dates) as mock_edit_dates:
            posts = scrape.attach_edit_dates(posts)
        mock_edit_dates.assert_called_once()
        for i, p in enumerate(posts):
            p.set_edit_date.assert_called_once_with(f'edit date {i+1}')

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