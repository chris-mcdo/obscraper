"""Tests for the post and extract_post modules."""

import unittest

import datetime

from obscraper import extract_post, post, download, utils
from test_extract import TEST_POST_NUMBERS


class TestPost(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.post_htmls = {
            number:
            download.grab_html_soup(
                f'https://www.overcomingbias.com/?p={number}')
            for number in TEST_POST_NUMBERS
        }

    def test_create_post_returns_valid_posts_for_valid_htmls(self):
        for html in self.post_htmls.values():
            p = post.create_post(html, votes=False, comments=False)
            self.assert_is_valid_post(p, votes=False, comments=False)

    def test_create_post_returns_valid_posts_for_valid_htmls_with_votes(self):
        for html in self.post_htmls.values():
            p = post.create_post(html, votes=True, comments=False)
            self.assert_is_valid_post(p, votes=True, comments=False)

    def test_create_post_returns_valid_posts_for_valid_htmls_with_comments(self):
        for html in self.post_htmls.values():
            p = post.create_post(html, votes=False, comments=True)
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
        self.assertIsInstance(test_post, post.Post)
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
        self.assertTrue(extract_post.is_valid_post_long_url(test_post.url))
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
        self.assertTrue(utils.is_aware_datetime(test_post.publish_date))
        # Word count and links
        self.assertNotEqual(test_post.plaintext, '')
        self.assertGreater(test_post.word_count, 5)
        [self.assertTrue(extract_post.is_valid_post_url(url))
         for url in test_post.internal_links.keys()]
        [self.assertGreaterEqual(number, 1)
         for number in test_post.internal_links.values()]
        [self.assertFalse(extract_post.is_valid_post_url(url))
         for url in test_post.external_links.keys()]
        [self.assertGreaterEqual(number, 1)
         for number in test_post.external_links.values()]
        # Disqus ID string
        self.assertTrue(extract_post.is_valid_disqus_id(test_post.disqus_id))
