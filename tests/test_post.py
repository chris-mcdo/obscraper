"""Tests for the post and extract_post modules."""

import unittest
from unittest.mock import MagicMock, patch
from obscraper import extract_post, post, download, utils
from obscraper.extract_post import OB_SERVER_TZ

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

    def assert_votes_and_comments_are_correct_for_post_27739(self, test_post):
        self.assertIsInstance(test_post.votes, int)
        self.assertIsInstance(test_post.comments, int)
        self.assertGreater(test_post.votes, TEST_POST_MIN_VOTES)
        self.assertGreater(test_post.comments, TEST_POST_MIN_COMMENTS)

    def assert_words_and_hyperlinks_are_correct_for_post_27739(self, test_post):
        self.assertEqual(test_post.words, 183)
        self.assertEqual(len(test_post.internal_links), 2)
        self.assertEqual(len(test_post.external_links), 3)

    def assert_post_has_no_votes_or_comments_attributes(self, test_post):
        self.assertFalse(hasattr(test_post, 'votes'))
        self.assertFalse(hasattr(test_post, 'comments'))

class TestIsOBPostURL(unittest.TestCase):
    # The two accepted formats look like this
    # https://www.overcomingbias.com/?p=32980
    # https://www.overcomingbias.com/2021/10/what-makes-stuff-rot.html
    def test_accepts_correctly_formatted_urls(self):
        is_url = extract_post.is_ob_post_url
        self.assertTrue(is_url('https://www.overcomingbias.com/?p=32980'))
        self.assertTrue(is_url('https://www.overcomingbias.com/2021/10/what-makes-stuff-rot.html'))

    def test_rejects_incorrectly_formatted_urls(self):
        is_url = extract_post.is_ob_post_url
        self.assertFalse(is_url('https://www.example.com/'))
        self.assertFalse(is_url('https://www.overcomingbias.com/p=32980'))
        self.assertFalse(is_url('https://www.overcomingbias.com/p=32980a'))
        self.assertFalse(is_url('https://www.overcomingbias.com/what-makes-stuff-rot.html'))
        self.assertFalse(is_url('https://www.overcomingbias.com/202/10/what-makes-stuff-rot.html'))
        self.assertFalse(is_url('https://www.overcomingbias.com/2021/10/what-makes-stuff-rot'))
        self.assertFalse(is_url('www.overcomingbias.com/2021/10/what-makes-stuff-rot'))

class TestDetermineOriginOfHTMLFiles(unittest.TestCase):    
    def test_is_page_from_origin_functions_work_with_ob_post(self):
        test_html = download.grab_html_soup('https://overcomingbias.com/?p=27739')
        self.assertTrue(extract_post.is_ob_site_html(test_html))
        self.assertTrue(extract_post.is_ob_post_html(test_html))

    def test_is_page_from_origin_functions_work_with_ob_page(self):
        test_html = download.grab_html_soup('https://www.overcomingbias.com/page/1')
        self.assertTrue(extract_post.is_ob_site_html(test_html))
        self.assertFalse(extract_post.is_ob_post_html(test_html))

    def test_is_page_from_origin_functions_work_with_ob_home_page(self):
        test_html = download.grab_html_soup('https://www.overcomingbias.com/')
        self.assertTrue(extract_post.is_ob_site_html(test_html))
        self.assertFalse(extract_post.is_ob_post_html(test_html))

    def test_is_page_from_origin_functions_work_with_example_dot_com_page(self):
        test_html = download.grab_html_soup('https://example.com/')
        self.assertFalse(extract_post.is_ob_site_html(test_html))
        self.assertFalse(extract_post.is_ob_post_html(test_html))

class TestHasPostInId(unittest.TestCase):
    def test_accepts_tags_with_correctly_formatted_strings(self):
        self.assertTrue(self.mock_tag_has_post_in_id(id_string='post-33847'))
        self.assertTrue(self.mock_tag_has_post_in_id(id_string='post-123'))

    def test_rejects_tags_with_incorrectly_formatted_strings(self):
        self.assertFalse(self.mock_tag_has_post_in_id(id_string=''))
        self.assertFalse(self.mock_tag_has_post_in_id(id_string='post'))

    def test_rejects_tags_without_id_attribute(self):
        self.assertFalse(self.mock_tag_has_post_in_id(has_id=False, id_string='post-33847'))

    def mock_tag_has_post_in_id(self, has_id=True, id_string=''):
        """Create a mock tag with specified id attribute."""
        tag = MagicMock()
        tag.has_attr.return_value = has_id
        tag.__getitem__.return_value = id_string
        return extract_post.has_post_in_id(tag)