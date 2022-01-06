import unittest
from unittest.mock import MagicMock
from obscraper import extract_page, download

class TestIsOBPostURL(unittest.TestCase):
    # The two accepted formats look like this
    # https://www.overcomingbias.com/?p=32980
    # https://www.overcomingbias.com/2021/10/what-makes-stuff-rot.html
    def test_accepts_correctly_formatted_urls(self):
        is_url = extract_page.is_ob_post_url
        self.assertTrue(is_url('https://www.overcomingbias.com/?p=32980'))
        self.assertTrue(is_url('https://www.overcomingbias.com/2021/10/what-makes-stuff-rot.html'))

    def test_rejects_incorrectly_formatted_urls(self):
        is_url = extract_page.is_ob_post_url
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
        self.assertTrue(extract_page.is_ob_site_html(test_html))
        self.assertTrue(extract_page.is_single_ob_post_html(test_html))
        self.assertFalse(extract_page.is_ob_page_html(test_html))

    def test_is_page_from_origin_functions_work_with_ob_page(self):
        test_html = download.grab_html_soup('https://www.overcomingbias.com/page/1')
        self.assertTrue(extract_page.is_ob_site_html(test_html))
        self.assertFalse(extract_page.is_single_ob_post_html(test_html))
        self.assertTrue(extract_page.is_ob_page_html(test_html))

    def test_is_page_from_origin_functions_work_with_ob_home_page(self):
        test_html = download.grab_html_soup('https://www.overcomingbias.com/')
        self.assertTrue(extract_page.is_ob_site_html(test_html))
        self.assertFalse(extract_page.is_single_ob_post_html(test_html))
        self.assertFalse(extract_page.is_ob_page_html(test_html))

    def test_is_page_from_origin_functions_work_with_example_dot_com_page(self):
        test_html = download.grab_html_soup('https://example.com/')
        self.assertFalse(extract_page.is_ob_site_html(test_html))
        self.assertFalse(extract_page.is_single_ob_post_html(test_html))
        self.assertFalse(extract_page.is_ob_page_html(test_html))

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
        return extract_page.has_post_in_id(tag)