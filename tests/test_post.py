"""Tests for the post and extract_post modules."""

import unittest
from unittest.mock import patch
from obscraper import extract_post, post, download, utils
from obscraper.extract_page import OB_SERVER_TZ

TEST_POST_NUMBER = 27739
TEST_POST_MIN_VOTES = 150
TEST_POST_MIN_COMMENTS = 100

class TestPost(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.post_html = download.grab_html_soup(f'https://overcomingbias.com/?p={TEST_POST_NUMBER}')

    def test_extracted_vote_auth_code_has_correct_format(self):
        vote_auth_code = extract_post.extract_vote_auth_code(self.post_html)
        self.assertRegex(vote_auth_code, r'^[a-z0-9]{10}$')

    def test_create_post_gives_correct_result_for_test_post(self):
        # Act
        p = post.create_post(self.post_html, votes=True, comments=True)
        # Assert
        self.assert_standard_attributes_are_correct_for_post_27739(p)
        self.assert_votes_and_comments_are_correct_for_post_27739(p)
        self.assert_words_and_hyperlinks_are_correct_for_post_27739(p)
        self.assertFalse(hasattr(p, 'edit_date'))

    def test_create_post_gives_correct_result_for_votes_and_comments(self):
        p = post.create_post(self.post_html, votes=False, comments=False)
        self.assert_standard_attributes_are_correct_for_post_27739(p)
        self.assert_post_has_no_votes_or_comments_attributes(p)
        self.assert_words_and_hyperlinks_are_correct_for_post_27739(p)
    
    def test_create_post_gives_correct_result_for_truncated_test_post(self):
        with patch('obscraper.extract_page.is_post_truncated', return_value=True) as mock_post_truncated:
            p = post.create_post(self.post_html, votes=False, comments=False)
        mock_post_truncated.assert_called_once()
        self.assert_post_has_no_words_or_hyperlinks_attributes(p)

    def test_create_post_gives_correct_result_for_moved_test_post(self):
        with patch('obscraper.extract_page.has_post_moved', return_value=True) as mock_has_post_moved:
            p = post.create_post(self.post_html, votes=False, comments=False)
        mock_has_post_moved.assert_called_once()
        self.assert_words_and_hyperlinks_are_correct_for_post_27739(p)
        self.assertTrue(p.has_moved)

    def test_create_post_gives_correct_result_after_edit_date_attached(self):
        p = post.create_post(self.post_html, votes=False, comments=False)
        p.set_edit_date('Fake date')
        self.assert_standard_attributes_are_correct_for_post_27739(p)
        self.assert_post_has_no_votes_or_comments_attributes(p)
        self.assert_words_and_hyperlinks_are_correct_for_post_27739(p)
        self.assertEqual(p.edit_date, 'Fake date')

    def assert_standard_attributes_are_correct_for_post_27739(self, test_post):
        self.assertIsInstance(test_post, post.Post)
        self.assertEqual(test_post.name, 'forget-911')
        self.assertEqual(test_post.number, TEST_POST_NUMBER)
        self.assertEqual(test_post.type, 'post')
        self.assertEqual(test_post.status, 'publish')
        self.assertEqual(test_post.format, 'standard')
        self.assertEqual(test_post.tags, ['death', 'signaling'])
        self.assertEqual(test_post.categories, ['uncategorized'])
        self.assertEqual(test_post.title, 'Forget 9/11')
        self.assertEqual(test_post.author, 'Robin Hanson')
        self.assertEqual(test_post.publish_date, utils.tidy_date('September 11, 2011 9:10 am', OB_SERVER_TZ))
        self.assertFalse(test_post.has_moved)

    def assert_votes_and_comments_are_correct_for_post_27739(self, test_post):
        self.assertIsInstance(test_post.votes, int)
        self.assertIsInstance(test_post.comments, int)
        self.assertGreater(test_post.votes, TEST_POST_MIN_VOTES)
        self.assertGreater(test_post.comments, TEST_POST_MIN_COMMENTS)

    def assert_words_and_hyperlinks_are_correct_for_post_27739(self, test_post):
        self.assertEqual(test_post.words, 183)
        self.assertEqual(len(test_post.internal_links), 2)
        self.assertEqual(len(test_post.external_links), 3)

    def assert_post_has_no_words_or_hyperlinks_attributes(self, test_post):
        self.assertFalse(hasattr(test_post, 'words'))
        self.assertFalse(hasattr(test_post, 'internal_links'))
        self.assertFalse(hasattr(test_post, 'external_links'))

    def assert_post_has_no_votes_or_comments_attributes(self, test_post):
        self.assertFalse(hasattr(test_post, 'votes'))
        self.assertFalse(hasattr(test_post, 'comments'))