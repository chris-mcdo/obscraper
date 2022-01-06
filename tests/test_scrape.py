
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
        self.assertRaises(ValueError, scrape.get_posts_by_url, url)

class TestGetPostsByDate(unittest.TestCase):
    def setUp(self):
        # Cleanup: unpatch once finished
        self.addCleanup(patch.stopall)

        # Useful dates and times
        utc=datetime.timezone.utc
        self.current_datetime = datetime.datetime.now()
        self.current_year = self.current_datetime.year
        self.current_month = self.current_datetime.month

        # Patch functions
        def grab_publish_dates(page):
            # Month number = current month (minus) page number 
            # Posts are published on days 2, 4, 6, ..., 20 of each month
            post_year = self.current_year + ((self.current_month - page - 1) // 12)
            post_month = 1 + ((self.current_month - page - 1) % 12)
            if datetime.datetime(post_year, post_month, 1, tzinfo=datetime.timezone.utc) < scrape.MIN_DATE:
                raise exceptions.InvalidResponseError
            # Fewer than 10 posts on the last page
            n_posts = 10 if (post_year, post_month) != (scrape.MIN_DATE.year, scrape.MIN_DATE.month) else 6
            return [datetime.datetime(year=post_year, month=post_month, day=20 - 2 * i, hour=14, tzinfo=utc) for i in range(n_posts)]
        def grab_all_posts_on_page(page):
            publish_dates = grab_publish_dates(page)
            page_posts = [MagicMock(url=f'page {page} post {i+1}', publish_date=date) for i, date in enumerate(publish_dates)]
            return page_posts
        def attach_edit_dates(post_list):
            for post in post_list:
                post.edit_date = 'Edit date set!'
            return post_list

        # Patch mocks
        self.mock_get_start_date = patch('obscraper.grab.grab_publish_dates', side_effect=grab_publish_dates).start()
        self.mock_grab_posts = patch('obscraper.grab.grab_all_posts_on_page', side_effect=grab_all_posts_on_page).start()
        self.mock_attach_edit_dates = patch('obscraper.scrape.attach_edit_dates', side_effect=attach_edit_dates).start()

    def test_returns_empty_list_when_end_date_before_2000(self):
        start_date = datetime.datetime(1998, 4, 19, tzinfo=datetime.timezone.utc)
        end_date = datetime.datetime(1999, 6, 2, tzinfo=datetime.timezone.utc)
        self.assertEqual(scrape.get_posts_by_date(start_date, end_date), [])

    def test_returns_empty_list_when_start_date_is_now(self):
        start_date = datetime.datetime.now(datetime.timezone.utc)
        self.assertEqual(scrape.get_posts_by_date(start_date), [])
    
    def test_returns_expected_result_with_no_end_date(self):
        n_months = 4
        start_year = self.current_year + ((self.current_month - n_months - 1) // 12)
        start_month = 1 + ((self.current_month - n_months - 1) % 12)
        start_date = datetime.datetime(year=start_year, month=start_month, day=1, tzinfo=datetime.timezone.utc)
        post_list = scrape.get_posts_by_date(start_date)
        self.assertIsInstance(post_list, list)
        for i, post in enumerate(post_list):
            self.assertEqual(post.url, f'page {1 + i // 10} post {1 + i % 10}')
            self.assertIsInstance(post.publish_date, datetime.datetime)
            self.assertEqual(post.edit_date, 'Edit date set!')

    def test_returns_expected_result_with_no_start_date(self):
        n_months = 35
        end_year = scrape.MIN_DATE.year + ((n_months + scrape.MIN_DATE.month - 1) // 12)
        end_month = 1 + (n_months + scrape.MIN_DATE.month - 1) % 12
        end_date = datetime.datetime(end_year, end_month, 1, tzinfo=datetime.timezone.utc)
        post_list = scrape.get_posts_by_date(end_date=end_date)
        self.assertEqual(len(post_list), 346)
        for post in post_list:
            self.assertIsInstance(post.publish_date, datetime.datetime)
            self.assertEqual(post.edit_date, 'Edit date set!')

    def test_returns_expected_result_with_start_and_end_dates(self):
        start_date = datetime.datetime(year=2011, month=8, day=13, tzinfo=datetime.timezone.utc)
        end_date = datetime.datetime(year=2013, month=2, day=5, tzinfo=datetime.timezone.utc)
        post_list = scrape.get_posts_by_date(start_date, end_date)
        self.assertEqual(len(post_list), 176)
        for post in post_list:
            self.assertIsInstance(post.publish_date, datetime.datetime)
            self.assertEqual(post.edit_date, 'Edit date set!')

    def test_returns_value_error_when_end_date_before_start_date(self):
        start_date = datetime.datetime(year=2015, month=8, day=13, tzinfo=datetime.timezone.utc)
        end_date = datetime.datetime(year=2013, month=2, day=5, tzinfo=datetime.timezone.utc)
        self.assertRaises(ValueError, scrape.get_posts_by_date, start_date=start_date, end_date=end_date)

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

    def test_works_as_expected_for_example_page(self):
        posts = grab.grab_all_posts_on_page(200)
        for p in posts:
            self.assertFalse(hasattr(p, 'edit_date'))
        posts = scrape.attach_edit_dates(posts)
        for p in posts:
            self.assertTrue(hasattr(p, 'edit_date'))

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

class TestRaiseExceptionIfDateHasIncorrectFormat(unittest.TestCase):
    def test_accepts_dates_with_correct_format(self):
        check_date = scrape.raise_exception_if_date_has_incorrect_format
        self.assertIsNone(check_date(None))
        self.assertIsNone(check_date(datetime.datetime.now(datetime.timezone.utc)))
    
    def test_rejects_date_with_incorrect_format(self):
        check_date = scrape.raise_exception_if_date_has_incorrect_format
        self.assertRaises(TypeError, check_date, 'Not a date')
        self.assertRaises(TypeError, check_date, datetime.datetime.now())
        self.assertRaises(TypeError, check_date, [datetime.datetime.now(datetime.timezone.utc)])