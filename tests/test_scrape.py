
import unittest
from unittest.mock import MagicMock, patch

import datetime

from obscraper import _exceptions, _extract_post, _grab, _post, _scrape, _utils


class TestGetAllPosts(unittest.TestCase):
    @patch('obscraper._grab.grab_edit_dates')
    def test_returns_correct_result_for_fake_edit_list(self, mock_grab_edit_dates):
        def tidy(d): return _utils.tidy_date(d, 'US/Eastern')
        edit_dates = {
            'https://www.overcomingbias.com/2006/11/introduction.html': tidy('November 22, 2006 6:17 am'),
            'https://www.overcomingbias.com/2007/10/a-rational-argu.html': tidy('October 5, 2007 2:31 pm'),
            'https://www.overcomingbias.com/2021/04/shoulda-listened-futures.html': tidy('July 2, 2021 9:15 am')
        }
        mock_grab_edit_dates.return_value = edit_dates
        posts = _scrape.get_all_posts()
        self.assertEqual(len(posts), 2)
        [self.assertEqual(p.edit_date, edit_dates[url])
         for url, p in posts.items()]


class TestGetPostByURL(unittest.TestCase):
    def test_returns_valid_post_for_valid_url(self):
        url = 'https://www.overcomingbias.com/2021/10/what-makes-stuff-rot.html'
        p = _scrape.get_post_by_url(url)
        self.assertIsInstance(p, _post.Post)
        self.assertEqual(p.url, url)

    def test_raises_exception_when_post_not_found(self):
        url = 'https://www.overcomingbias.com/2016/03/not-a-real-post.html'
        self.assertRaises(_exceptions.InvalidResponseError,
                          _scrape.get_post_by_url, url)


class TestGetPostsByURLs(unittest.TestCase):
    def test_returns_valid_posts_for_valid_urls(self):
        urls = [
            'https://www.overcomingbias.com/2021/10/what-makes-stuff-rot.html',
            'https://www.overcomingbias.com/2014/07/limits-on-generality.html',
            'https://www.overcomingbias.com/2012/02/why-retire.html'
        ]
        posts = _scrape.get_posts_by_urls(urls)
        self.assertIsInstance(posts, dict)
        self.assertTrue(len(posts), len(urls))
        for p in posts.values():
            self.assert_is_valid_post(p)
            self.assertIn(p.url, urls)

    def test_raises_type_error_if_urls_are_wrong_type(self):
        for urls in [
            ['https://www.overcomingbias.com/2007/10/a-rational-argu.html', None],
            [3514, 8293],
        ]:
            self.assertRaises(TypeError, _scrape.get_posts_by_urls, urls)

    def test_raises_value_error_if_urls_in_wrong_format(self):
        for urls in [
            ['Not a URL'],
            ['https://example.com/'],
            ['http://overcomingbias.com/'],
            ['https://www.overcomingbias.com/post.xml'],
            ['https://www.overcomingbias.com/page/20'],
            ['http://www.overcomingbias.com/archives'],
        ]:
            self.assertRaises(ValueError, _scrape.get_posts_by_urls, urls)

    def test_returns_none_for_invalid_urls(self):
        urls = [
            'https://www.overcomingbias.com/2007/10/a-rational-argu.html',  # LessWrong URL
            'https://www.overcomingbias.com/2012/08/not-a-real-post.html',  # Fake URL
            r'https://www.overcomingbias.com/2007/01/the-procrastinator%e2%80%99s-clock.html',  # valid URL
        ]
        posts = _scrape.get_posts_by_urls(urls)
        self.assertIsNone(posts[urls[0]])
        self.assertIsNone(posts[urls[1]])
        self.assert_is_valid_post(posts[urls[2]])

    def assert_is_valid_post(self, p):
        self.assertIsInstance(p, _post.Post)
        self.assertGreaterEqual(p.word_count, 5)
        self.assertGreaterEqual(p.votes, 0)
        self.assertGreaterEqual(p.comments, 0)


class TestGetPostsByEditDate(unittest.TestCase):
    def test_returns_valid_results_for_valid_arguments(self):
        with patch('obscraper._grab.grab_edit_dates', return_value=_grab.grab_edit_dates()) as mock_grab_edit_dates:
            now = datetime.datetime.now(datetime.timezone.utc)
            dday = datetime.timedelta(days=1)
            self.assertEqual(_scrape.get_posts_by_edit_date(
                now+dday, now+5*dday), {})
            last_week = _scrape.get_posts_by_edit_date(now-7*dday, now)
            self.assertIsInstance(last_week, dict)
            [self.assertTrue(_extract_post.is_valid_post_url(url))
             for url in last_week.keys()]
            [self.assertIsInstance(p, _post.Post) for p in last_week.values()]

    def test_raises_type_error_if_dates_are_wrong_type(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        dday = datetime.timedelta(days=1)
        self.assertRaises(TypeError, _scrape.get_posts_by_edit_date,
                          start_date=now, end_date=datetime.datetime.now())
        self.assertRaises(TypeError, _scrape.get_posts_by_edit_date,
                          start_date=now - 3 * dday, end_date='hi')
        self.assertRaises(TypeError, _scrape.get_posts_by_edit_date,
                          start_date=12345, end_date=now)

    def test_raises_value_error_if_end_date_before_start_date(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        dday = datetime.timedelta(days=1)
        self.assertRaises(ValueError, _scrape.get_posts_by_edit_date,
                          start_date=now+dday, end_date=now-dday)


class TestGetVotes(unittest.TestCase):
    def test_returns_valid_vote_counts_for_valid_post_numbers(self):
        post_numbers = {
            'https://www.overcomingbias.com/2006/11/introduction.html': 18402,
            'https://www.overcomingbias.com/2007/03/the_very_worst_.html': 18141,
            'https://www.overcomingbias.com/2009/05/we-only-need-a-handshake.html': 18423,
            'https://www.overcomingbias.com/2021/04/shoulda-listened-futures.html': 32811,
            'https://www.overcomingbias.com/2021/12/innovation-liability-nightmare.html': 33023,
        }
        votes = _scrape.get_votes(post_numbers)
        for label, vote in votes.items():
            self.assertIn(label, post_numbers.keys())
            self.assertIsInstance(vote, int)
            self.assertGreaterEqual(vote, 0)

    def test_raises_type_error_if_arguments_are_wrong_type(self):
        for post_numbers in [
            18402,
            {
                'https://www.overcomingbias.com/2006/11/introduction.html': 18402,
                12345: 45678
            },
            {
                'https://www.overcomingbias.com/2009/05/we-only-need-a-handshake.html': 18423,
                'https://www.overcomingbias.com/2021/04/shoulda-listened-futures.html': 'Rogue string',
            },
        ]:
            self.assertRaises(TypeError, _scrape.get_votes, post_numbers)

    def test_raises_value_error_if_arguments_have_wrong_value(self):
        for post_numbers in [
            {
                'intro': 18402,
                'new': 4567
            },
            {
                'https://www.overcomingbias.com/2009/05/we-only-need-a-handshake.html': 18423,
                'https://www.overcomingbias.com/2021/04/shoulda-listened-futures.html': 123456,
            },
        ]:
            self.assertRaises(ValueError, _scrape.get_votes, post_numbers)


class TestGetComments(unittest.TestCase):
    def test_returns_valid_comment_counts_for_valid_disqus_ids(self):
        disqus_ids = {
            'https://www.overcomingbias.com/2006/11/introduction.html':
            '18402 http://prod.ob.trike.com.au/2006/11/how-to-join.html',
            'https://www.overcomingbias.com/2007/03/the_very_worst_.html':
            '18141 http://prod.ob.trike.com.au/2007/03/the-very-worst-kind-of-bias.html',
            'https://www.overcomingbias.com/2009/05/we-only-need-a-handshake.html':
            '18423 http://www.overcomingbias.com/?p=18423',
            'https://www.overcomingbias.com/2021/04/shoulda-listened-futures.html':
            '32811 http://www.overcomingbias.com/?p=32811',
            'https://www.overcomingbias.com/2021/12/innovation-liability-nightmare.html':
            '33023 https://www.overcomingbias.com/?p=33023',
        }
        comments = _scrape.get_comments(disqus_ids)
        for label, comment in comments.items():
            self.assertIn(label, disqus_ids.keys())
            self.assertIsInstance(comment, int)
            self.assertGreater(comment, 1)

    def test_raises_type_error_if_arguments_are_wrong_type(self):
        for disqus_ids in [
            '18402 http://prod.ob.trike.com.au/2006/11/how-to-join.html',
            {
                'https://www.overcomingbias.com/2006/11/introduction.html':
                '18402 http://prod.ob.trike.com.au/2006/11/how-to-join.html',
                'https://www.overcomingbias.com/2007/03/the_very_worst_.html':
                18481,
            },
            {
                'https://www.overcomingbias.com/2009/05/we-only-need-a-handshake.html':
                '18423 http://www.overcomingbias.com/?p=18423',
                35618:
                '32811 http://www.overcomingbias.com/?p=32811',
            }
        ]:
            self.assertRaises(TypeError, _scrape.get_comments, disqus_ids)

    def test_raises_value_error_if_arguments_have_wrong_value(self):
        dt = _utils.tidy_date('October 15, 2013 6:10 pm', 'US/Eastern')
        for disqus_ids in [
            {
                'https://www.overcomingbias.com/2006/11/introduction.html':
                '18402 http://prod.ob.trike.com.au/2006/11/how-to-join.html',
                'https://www.overcomingbias.com/2007/03/the_very_worst_.html':
                '18141 http://prod.ob.trike.com.au/?p=18141',
            },
            {'https://www.overcomingbias.com/2006/11/introduction.html': ''},
        ]:
            self.assertRaises(ValueError, _scrape.get_comments, disqus_ids)

    def test_returns_none_for_invalid_numbers(self):
        none_urls = [
            'https://www.overcomingbias.com/2007/03/the_very_worst_.html',
            'https://www.overcomingbias.com/2021/04/shoulda-listened-futures.html',
        ]
        real_urls = [
            'https://www.overcomingbias.com/2009/05/we-only-need-a-handshake.html']
        disqus_ids = {
            'https://www.overcomingbias.com/2007/03/the_very_worst_.html':
            '12345 http://prod.ob.trike.com.au/2007/03/the-very-worst-kind-of-bias.html',
            'https://www.overcomingbias.com/2009/05/we-only-need-a-handshake.html':
            '18423 http://www.overcomingbias.com/?p=18423',
            'https://www.overcomingbias.com/2021/04/shoulda-listened-futures.html':
            '65432 http://www.overcomingbias.com/?p=65432',
        }
        comments = _scrape.get_comments(disqus_ids)
        for url in none_urls:
            self.assertIsNone(comments[url])
        for url in real_urls:
            self.assertIsInstance(comments[url], int)
            self.assertGreater(comments[url], 1)


class TestAttachEditDates(unittest.TestCase):
    def test_returns_post_with_date_attached_for_fake_posts_and_dates(self):
        # Expect more edit dates than posts
        edit_dates = {f'url {i+1}': f'edit date {i+1}' for i in range(10)}
        posts = {f'url {2*i+2}': MagicMock(url=f'url {2*i+2}')
                 for i in range(5)}
        with patch('obscraper._grab.grab_edit_dates', return_value=edit_dates) as mock_edit_dates:
            posts = _scrape.attach_edit_dates(posts)
        mock_edit_dates.assert_called_once()
        for i, p in enumerate(posts.values()):
            self.assertEqual(p.edit_date, f'edit date {2*i+2}')

    def test_returns_none_for_invalid_post(self):
        # Posts which could not be found are returned as None
        edit_dates = {'fake url': 'fake edit date'}
        with patch('obscraper._grab.grab_edit_dates', return_value=edit_dates) as mock_edit_dates:
            invalid_post = _scrape.attach_edit_dates({'fake url': None})
        mock_edit_dates.assert_called_once()
        self.assertIsNone(invalid_post['fake url'])


class TestRaiseExceptionIfNumberHasIncorrectFormat(unittest.TestCase):
    def test_no_exception_raised_if_number_has_correct_format(self):
        check_number = _scrape.raise_exception_if_number_has_incorrect_format
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
        check_number = _scrape.raise_exception_if_number_has_incorrect_format
        self.assertRaises(TypeError, check_number, 'Hello')
        self.assertRaises(TypeError, check_number, ['A', 'List'])
        self.assertRaises(TypeError, check_number, 32.591)
        self.assertRaises(TypeError, check_number, [12345])

    def test_value_error_raised_if_number_is_not_5_digits(self):
        check_number = _scrape.raise_exception_if_number_has_incorrect_format
        self.assertRaises(ValueError, check_number, 1)
        self.assertRaises(ValueError, check_number, 9999)
        self.assertRaises(ValueError, check_number, 100000)
        self.assertRaises(ValueError, check_number, -12594)


class TestClearCache(unittest.TestCase):
    @patch('obscraper._extract_post.is_ob_post_html', return_value=True)
    def test_clears_grab_post_cache(self, mock_is_ob_post):
        _scrape.clear_cache()

        p1 = _grab.grab_post_by_url(
            'https://www.overcomingbias.com/2021/12/innovation-liability-nightmare.html')
        self.assertIsInstance(p1, _post.Post)
        mock_is_ob_post.assert_called_once()

        p2 = _grab.grab_post_by_url(
            'https://www.overcomingbias.com/2021/12/innovation-liability-nightmare.html')
        self.assertEqual(p1, p2)
        mock_is_ob_post.assert_called_once()

        _scrape.clear_cache()

        p3 = _grab.grab_post_by_url(
            'https://www.overcomingbias.com/2021/12/innovation-liability-nightmare.html')
        self.assertEqual(mock_is_ob_post.call_count, 2)
