
import unittest
from unittest.mock import MagicMock, patch

import datetime

from obscraper import _exceptions, _extract_post, _grab, _post, _scrape, _utils


class TestGetAllPosts(unittest.TestCase):
    @patch('obscraper._grab.grab_edit_dates')
    def test_returns_correct_result_for_fake_edit_list(self, mock_grab_edit_dates):
        def tidy(d):
            return _utils.tidy_date(d, 'US/Eastern')
        edit_dates = {
            '/2006/11/introduction': tidy('November 22, 2006 6:17 am'),
            '/2007/10/a-rational-argu': tidy('October 5, 2007 2:31 pm'),
            '/2021/04/shoulda-listened-futures': tidy('July 2, 2021 9:15 am')
        }
        mock_grab_edit_dates.return_value = edit_dates
        posts = _scrape.get_all_posts()
        self.assertEqual(len(posts), 2)
        for name, p in posts.items():
            self.assertEqual(p.edit_date, edit_dates[name])


class TestGetPostByURL(unittest.TestCase):
    def setUp(self):
        fake_posts = {
            '/2006/11/introduction': 1,
            '/2021/10/what-makes-stuff-rot': 2,
            '/2014/07/limits-on-generality': 3,
        }
        patch_grab_post = patch('obscraper._grab.grab_post_by_name',
                                side_effect=lambda v: fake_posts.get(v, None))
        patch_attach_dates = patch('obscraper._scrape.attach_edit_dates',
                                   side_effect=lambda v: v)
        self.mock_grab_post = patch_grab_post.start()
        self.mock_attach_dates = patch_attach_dates.start()
        self.addCleanup(patch.stopall)

    def test_raises_type_error_if_url_is_wrong_type(self):
        for url in [None, 35]:
            self.assertRaises(TypeError, _scrape.get_post_by_url, url)

    def test_raises_value_error_if_url_in_wrong_format(self):
        for url in [
            'Not a url',
            'https://www.overcomingbias.com/?p=12345',
            'https://www.overcomingbias.com/abc/de/fg.html',
            'https://www.overcomingbias.com/1234/56/ab',
            'https://www.overcomingbias.com/archives',
        ]:
            self.assertRaises(ValueError, _scrape.get_post_by_url, url)

    def test_raises_error_when_post_not_found(self):
        url = 'https://www.overcomingbias.com/2021/10/not-a-real-post.html'
        self.assertRaises(_exceptions.InvalidResponseError, _scrape.get_post_by_url, url)

    def test_returns_valid_posts_for_valid_urls(self):
        url = 'https://www.overcomingbias.com/2021/10/what-makes-stuff-rot.html'
        p = _scrape.get_post_by_url(url)
        self.assertEqual(p, 2)

class TestGetPostByName(unittest.TestCase):
    def setUp(self):
        fake_posts = {
            '/2006/11/introduction': 1,
            '/2021/10/what-makes-stuff-rot': 2,
            '/2014/07/limits-on-generality': 3,
        }
        patch_grab_post = patch('obscraper._grab.grab_post_by_name',
                                side_effect=lambda v: fake_posts.get(v, None))
        patch_attach_dates = patch('obscraper._scrape.attach_edit_dates',
                                   side_effect=lambda v: v)
        self.mock_grab_post = patch_grab_post.start()
        self.mock_attach_dates = patch_attach_dates.start()
        self.addCleanup(patch.stopall)

    def test_raises_type_error_if_name_is_wrong_type(self):
        for name in [None, 35]:
            self.assertRaises(TypeError, _scrape.get_post_by_name, name)

    def test_raises_value_error_if_name_in_wrong_format(self):
        for name in [
            'Not a name',
            '/?p=12345',
            '/abc/de/fg.html',
            '/archives',
        ]:
            self.assertRaises(ValueError, _scrape.get_post_by_name, name)

    def test_raises_error_when_post_not_found(self):
        name = '/2021/10/not-a-real-post'
        self.assertRaises(_exceptions.InvalidResponseError, _scrape.get_post_by_name, name)

    def test_returns_valid_posts_for_valid_names(self):
        name = '/2021/10/what-makes-stuff-rot'
        p = _scrape.get_post_by_name(name)
        self.assertEqual(p, 2)

class TestGetPostsByNames(unittest.TestCase):
    def test_returns_valid_posts_for_valid_names(self):
        names = [
            '/2021/10/what-makes-stuff-rot',
            '/2014/07/limits-on-generality',
            r'/2007/01/the-procrastinator%e2%80%99s-clock',  # valid
        ]
        posts = _scrape.get_posts_by_names(names)
        self.assertIsInstance(posts, dict)
        self.assertTrue(len(posts), len(names))
        for p in posts.values():
            self.assert_is_valid_post(p)
            self.assertIn(p.name, names)

    def test_returns_empty_dict_for_empty_list(self):
        names = []
        posts = _scrape.get_posts_by_names(names)
        self.assertEqual(posts, {})

    def test_raises_type_error_if_names_are_wrong_type(self):
        for names in [
            ['/2007/10/a-rational-argu', None],
            [3514, 8293],
        ]:
            self.assertRaises(TypeError, _scrape.get_posts_by_names, names)

    def test_raises_value_error_if_names_in_wrong_format(self):
        for names in [
            ['Not a name'],
            ['/'],
            ['/123/456/ok'],
            ['/post'],
            ['/page/20/post'],
            ['/archives'],
        ]:
            self.assertRaises(ValueError, _scrape.get_posts_by_names, names)

    def test_returns_none_for_nonexistent_names(self):
        names = [
            '/2007/10/a-rational-argu',  # LessWrong
            '/2012/08/not-a-real-post',  # Fake
            '/2012/02/why-retire',  # Valid
        ]
        posts = _scrape.get_posts_by_names(names)
        self.assertIsNone(posts[names[0]])
        self.assertIsNone(posts[names[1]])
        self.assert_is_valid_post(posts[names[2]])

    def assert_is_valid_post(self, p):
        self.assertIsInstance(p, _post.Post)
        self.assertGreaterEqual(p.word_count, 5)
        self.assertGreaterEqual(p.votes, 0)
        self.assertGreaterEqual(p.comments, 0)


class TestGetPostsByURLs(unittest.TestCase):
    def setUp(self):
        fake_posts = {
            '/2006/11/introduction': 1,
            '/2021/10/what-makes-stuff-rot': 2,
            '/2014/07/limits-on-generality': 3,
        }
        patch_grab_post = patch('obscraper._grab.grab_post_by_name',
                                side_effect=lambda v: fake_posts.get(v, None))
        patch_attach_dates = patch('obscraper._scrape.attach_edit_dates',
                                   side_effect=lambda v: v)
        self.mock_grab_post = patch_grab_post.start()
        self.mock_attach_dates = patch_attach_dates.start()
        self.addCleanup(patch.stopall)

    def test_returns_empty_dict_for_empty_list(self):
        urls = []
        posts = _scrape.get_posts_by_urls(urls)
        self.assertEqual(posts, {})

    def test_raises_type_error_if_urls_are_wrong_type(self):
        for urls in [
            ['https://www.overcomingbias.com/2021/10/what-makes-stuff-rot.html', None],
            [3514, 8293],
        ]:
            self.assertRaises(TypeError, _scrape.get_posts_by_urls, urls)

    def test_raises_value_error_if_urls_in_wrong_format(self):
        for urls in [
            ['Not a url'],
            ['https://www.overcomingbias.com/?p=12345'],
            ['https://www.overcomingbias.com/abc/de/fg.html'],
            ['https://www.overcomingbias.com/1234/56/ab'],
            ['https://www.overcomingbias.com/page/20/'],
            ['https://www.overcomingbias.com/archives'],
        ]:
            self.assertRaises(ValueError, _scrape.get_posts_by_urls, urls)

    def test_returns_valid_posts_for_valid_urls(self):
        urls = [
            'https://www.overcomingbias.com/2021/10/what-makes-stuff-rot.html',
            'https://www.overcomingbias.com/2015/08/not-a-real-post.html',
        ]
        posts = _scrape.get_posts_by_urls(urls)
        self.assertIsInstance(posts, dict)
        self.assertEqual(len(posts), 2)
        self.assertEqual(posts[urls[0]], 2)
        self.assertIsNone(posts[urls[1]])


class TestGetPostsByEditDate(unittest.TestCase):
    def test_returns_valid_results_for_valid_arguments(self):
        with patch('obscraper._grab.grab_edit_dates', return_value=_grab.grab_edit_dates()) as mock_grab_edit_dates:
            now = datetime.datetime.now(datetime.timezone.utc)
            dday = datetime.timedelta(days=1)
            self.assertEqual(_scrape.get_posts_by_edit_date(
                now+dday, now+5*dday), {})
            last_week = _scrape.get_posts_by_edit_date(now-7*dday, now)
            self.assertIsInstance(last_week, dict)
            [self.assertTrue(_extract_post.is_valid_post_name(name))
             for name in last_week.keys()]
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

    def test_calls_map_with_delay_with_correct_arguments(self):
        with patch('obscraper._future.map_with_delay') as mock_map_with_delay:
            intro_number = {'intro': 18402}
            mock_map_with_delay.return_value = 5
            fake_votes = _scrape.get_votes(intro_number, max_workers=3)
        mock_map_with_delay.assert_called_once()
        self.assertEqual(mock_map_with_delay.call_args.args[1], intro_number)
        self.assertEqual(
            mock_map_with_delay.call_args.kwargs['max_workers'], 3)
        self.assertEqual(fake_votes, 5)

    def test_exception_raised_when_invalid_max_workers_passed(self):
        get_votes = _scrape.get_votes
        intro_numbers = {'intro': 18402}
        self.assertRaises(TypeError, get_votes,
                          intro_numbers, max_workers='string')
        self.assertRaises(ValueError, get_votes,
                          intro_numbers, max_workers=-0.5)


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
        edit_dates = {f'name {i+1}': f'edit date {i+1}' for i in range(10)}
        posts = {}
        for i in range(5):
            # name attribute is special for mocks - it must be set after init
            mock = MagicMock()
            mock.name=f'name {2*i+2}'
            posts[f"name {2*i+2}"] = mock
        with patch('obscraper._grab.grab_edit_dates', return_value=edit_dates) as mock_edit_dates:
            posts = _scrape.attach_edit_dates(posts)
        mock_edit_dates.assert_called_once()
        for i, p in enumerate(posts.values()):
            self.assertEqual(p.edit_date, f'edit date {2*i+2}')

    def test_returns_none_for_invalid_post(self):
        # Posts which could not be found are returned as None
        edit_dates = {'fake name': 'fake edit date'}
        with patch('obscraper._grab.grab_edit_dates', return_value=edit_dates) as mock_edit_dates:
            invalid_post = _scrape.attach_edit_dates({'fake name': None})
        mock_edit_dates.assert_called_once()
        self.assertIsNone(invalid_post['fake name'])


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

        p1 = _grab.grab_post_by_name('/2021/12/innovation-liability-nightmare')
        self.assertIsInstance(p1, _post.Post)
        mock_is_ob_post.assert_called_once()

        p2 = _grab.grab_post_by_name('/2021/12/innovation-liability-nightmare')
        self.assertEqual(p1, p2)
        mock_is_ob_post.assert_called_once()

        _scrape.clear_cache()

        p3 = _grab.grab_post_by_name('/2021/12/innovation-liability-nightmare')
        self.assertEqual(mock_is_ob_post.call_count, 2)
