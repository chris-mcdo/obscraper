import unittest

import datetime

import obscraper
from obscraper import _post
from obscraper import _utils
from obscraper import _extract_post


@unittest.skip('skip expensive system tests')
class TestOBScraper(unittest.TestCase):
    def test_get_first_year_of_posts(self):
        # Arrange
        first_date = datetime.datetime(
            2006, 10, 1, tzinfo=datetime.timezone.utc)
        dweek = datetime.timedelta(weeks=1)

        # Act
        all_posts = obscraper.get_posts_by_edit_date(
            first_date, first_date + 52 * dweek)
        posts = [p for p in all_posts.values() if p is not None]
        posts = self.attach_comments_and_votes(posts)

        # Assert
        [self.assert_is_valid_post(p, votes=True, comments=True)
         for p in posts]

    def test_get_last_year_of_posts(self):
        now = datetime.datetime.now(datetime.timezone.utc)
        dweek = datetime.timedelta(weeks=1)

        # Act
        all_posts = obscraper.get_posts_by_edit_date(now - 52 * dweek, now)
        posts = [p for p in all_posts.values() if p is not None]
        posts = self.attach_comments_and_votes(posts)

        # Assert
        [self.assert_is_valid_post(p, votes=True, comments=True)
         for p in posts]

    def attach_comments_and_votes(self, posts):
        comments = obscraper.get_comments({p.url: p.disqus_id for p in posts})
        votes = obscraper.get_votes({p.url: p.number for p in posts})
        for p in posts:
            p.votes = votes[p.url]
            p.comments = comments[p.url]
        return posts

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
