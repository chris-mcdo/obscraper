
import unittest

import bs4

from obscraper import exceptions, extract_post, download, utils

TEST_POST_NUMBERS = [
    18402, # first post
    18141, # early post by another author
    18423, # just before Disqus API changes 
    32811, # just before Disqus API changes for 2nd time
    33023, # recent RH post
]

class TestExtractFunctionsOnExamplePosts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.post_htmls = {
            number: 
            download.grab_html_soup(f'https://www.overcomingbias.com/?p={number}') 
            for number in TEST_POST_NUMBERS
        }
    
    def test_extract_url_returns_correct_results_for_valid_htmls(self):
        url = self.function_to_get_attribute_by_number(extract_post.extract_url)
        self.assertEqual(url(18402), 'https://www.overcomingbias.com/2006/11/introduction.html')
        self.assertEqual(url(18141), 'https://www.overcomingbias.com/2007/03/the_very_worst_.html')
        self.assertEqual(url(18423), 'https://www.overcomingbias.com/2009/05/we-only-need-a-handshake.html')
        self.assertEqual(url(32811), 'https://www.overcomingbias.com/2021/04/shoulda-listened-futures.html')
        self.assertEqual(url(33023), 'https://www.overcomingbias.com/2021/12/innovation-liability-nightmare.html')

    def test_extract_name_returns_correct_results_for_valid_htmls(self):
        name = self.function_to_get_attribute_by_number(extract_post.extract_name)
        self.assertEqual(name(18402), 'introduction')
        self.assertEqual(name(18141), 'the_very_worst_')
        self.assertEqual(name(18423), 'we-only-need-a-handshake')
        self.assertEqual(name(32811), 'shoulda-listened-futures')
        self.assertEqual(name(33023), 'innovation-liability-nightmare')

    def test_extract_title_returns_correct_results_for_valid_htmls(self):
        title = self.function_to_get_attribute_by_number(extract_post.extract_title)
        self.assertEqual(title(18402), 'How To Join')
        self.assertEqual(title(18141), 'The Very Worst Kind of Bias')
        self.assertEqual(title(18423), 'Just A Handshake')
        self.assertEqual(title(32811), 'Shoulda-Listened Futures')
        self.assertEqual(title(33023), 'Innovation Liability Nightmare')

    def test_extract_author_returns_correct_results_for_valid_htmls(self):
        author = self.function_to_get_attribute_by_number(extract_post.extract_author)
        self.assertEqual(author(18402), 'Robin Hanson')
        self.assertEqual(author(18141), 'David J. Balan')
        self.assertEqual(author(18423), 'Robin Hanson')
        self.assertEqual(author(32811), 'Robin Hanson')
        self.assertEqual(author(33023), 'Robin Hanson')

    def test_extract_publish_date_returns_correct_results_for_valid_htmls(self):
        publish_date = self.function_to_get_attribute_by_number(extract_post.extract_publish_date)
        tidy = lambda d: utils.tidy_date(d, 'US/Eastern')
        self.assertEqual(publish_date(18402), tidy('November 20, 2006 6:00 am'))
        self.assertEqual(publish_date(18141), tidy('March 26, 2007 8:53 am'))
        self.assertEqual(publish_date(18423), tidy('May 26, 2009 2:00 pm'))
        self.assertEqual(publish_date(32811), tidy('April 27, 2021 6:45 pm'))
        self.assertEqual(publish_date(33023), tidy('December 26, 2021 1:10 pm'))

    def test_extract_number_returns_correct_results_for_valid_htmls(self):
        number = self.function_to_get_attribute_by_number(extract_post.extract_number)
        self.assertEqual(number(18402), 18402)
        self.assertEqual(number(18141), 18141)
        self.assertEqual(number(18423), 18423)
        self.assertEqual(number(32811), 32811)
        self.assertEqual(number(33023), 33023)

    def test_extract_tags_returns_correct_results_for_valid_htmls(self):
        tags = self.function_to_get_attribute_by_number(extract_post.extract_tags)
        self.assertEqual(tags(18402), ['meta'])
        self.assertEqual(tags(18141), ['morality', 'psychology'])
        self.assertEqual(tags(18423), ['signaling', 'social-science'])
        self.assertEqual(tags(32811), ['academia', 'prediction-markets', 'project'])
        self.assertEqual(tags(33023), ['innovation', 'law'])

    def test_extract_categories_returns_correct_results_for_valid_htmls(self):
        categories = self.function_to_get_attribute_by_number(extract_post.extract_categories)
        self.assertEqual(categories(18402), ['meta'])
        self.assertEqual(categories(18141), ['morality', 'psychology'])
        self.assertEqual(categories(18423), ['signaling', 'social-science'])
        self.assertEqual(categories(32811), ['uncategorized'])
        self.assertEqual(categories(33023), ['uncategorized'])

    def test_extract_type_returns_correct_results_for_valid_htmls(self):
        type = self.function_to_get_attribute_by_number(extract_post.extract_type)
        for number in [18402, 18141, 18423, 32811, 33023,]:
            self.assertEqual(type(number), 'post')

    def test_extract_status_returns_correct_results_for_valid_htmls(self):
        status = self.function_to_get_attribute_by_number(extract_post.extract_status)
        for number in [18402, 18141, 18423, 32811, 33023,]:
            self.assertEqual(status(number), 'publish')

    def test_extract_format_returns_correct_results_for_valid_htmls(self):
        format = self.function_to_get_attribute_by_number(extract_post.extract_format)
        for number in [18402, 18141, 18423, 32811, 33023,]:
            self.assertEqual(format(number), 'standard')

    def test_extract_word_count_returns_correct_results_for_valid_htmls(self):
        words = self.function_to_get_attribute_by_number(extract_post.extract_word_count)
        self.assertEqual(words(18402), 263)
        self.assertEqual(words(18141), 315)
        self.assertEqual(words(18423), 247)
        self.assertEqual(words(32811), 1205)
        self.assertEqual(words(33023), 387)

    def test_extract_internal_links_returns_correct_results_for_valid_htmls(self):
        internal_links = self.function_to_get_attribute_by_number(extract_post.extract_internal_links)
        self.assertEqual(internal_links(18402), {
            'http://www.overcomingbias.com/2006/12/contributors_be.html': 1,
            'http://www.overcomingbias.com/2007/02/moderate_modera.html': 1,
        })
        self.assertEqual(internal_links(18141), {})
        self.assertEqual(internal_links(18423), {})
        self.assertEqual(internal_links(32811), {})
        self.assertEqual(internal_links(33023), {
            'https://www.overcomingbias.com/2021/11/will-world-government-rot.html': 1,
            'https://www.overcomingbias.com/2011/07/innovation-a-growth-industry.html': 1,
            'https://www.overcomingbias.com/2020/04/vouch-for-pandemic-passports.html': 1
        })

    def test_extract_external_links_returns_correct_results_for_valid_htmls(self):
        external_links = self.function_to_get_attribute_by_number(extract_post.extract_external_links)
        self.assertEqual(external_links(18402), {
            'http://www.fhi.ox.ac.uk/': 1,
        })
        self.assertEqual(external_links(18141), {
            'http://www.solstice.us/russell/religionciv.html': 1,
            'http://www.davidbrin.com/addiction.html': 1,
        })
        self.assertEqual(external_links(18423), {
            'http://dx.doi.org/10.1016/j.geb.2009.05.001': 1
        })
        self.assertEqual(external_links(32811), {})
        self.assertEqual(external_links(33023), {
            'https://twitter.com/robinhanson/status/1474573132619001856': 1,
            'https://mason.gmu.edu/~rhanson/negliab.html': 1,
        })

    def test_extract_auth_code_returns_result_in_correct_format(self):
        code = self.function_to_get_attribute_by_number(extract_post.extract_vote_auth_code)
        for number in [18402, 18141, 18423, 32811, 33023,]:
            c = code(number)
            self.assertIsInstance(c, str)
            self.assertRegex(c, r'^[a-z0-9]{10}$')

    def test_extract_auth_code_returns_same_result_for_each_post(self):
        code = self.function_to_get_attribute_by_number(extract_post.extract_vote_auth_code)
        unique_codes = set([code(number) for number in [18402, 18141, 18423, 32811, 33023,]])
        self.assertEqual(len(unique_codes), 1)
        self.assertRegex(unique_codes.pop(), r'^[a-z0-9]{10}$')

    def test_extract_disqus_id_returns_correct_results_for_valid_htmls(self):
        disqus_id = self.function_to_get_attribute_by_number(extract_post.extract_disqus_id)
        self.assertEqual(disqus_id(18402), '18402 http://prod.ob.trike.com.au/2006/11/how-to-join.html')
        self.assertEqual(disqus_id(18141), '18141 http://prod.ob.trike.com.au/2007/03/the-very-worst-kind-of-bias.html')
        self.assertEqual(disqus_id(18423), '18423 http://www.overcomingbias.com/?p=18423')
        self.assertEqual(disqus_id(32811), '32811 http://www.overcomingbias.com/?p=32811')
        self.assertEqual(disqus_id(33023), '33023 https://www.overcomingbias.com/?p=33023')

    def function_to_get_attribute_by_number(self, extract_func):
        def func(number):
            return extract_func(self.post_htmls[number])
        return func

class TestExtractFunctionsOnFakePost(unittest.TestCase):
    def test_extract_functions_raise_exception_for_invalid_html(self):
        fake_html = bs4.BeautifulSoup('Fake HTML')
        not_found = exceptions.AttributeNotFoundError
        self.assertRaises(not_found, extract_post.extract_url, fake_html)
        self.assertRaises(not_found, extract_post.extract_name, fake_html)
        self.assertRaises(not_found, extract_post.extract_title, fake_html)
        self.assertRaises(not_found, extract_post.extract_author, fake_html)
        self.assertRaises(not_found, extract_post.extract_publish_date, fake_html)
        self.assertRaises(not_found, extract_post.extract_number, fake_html)
        self.assertRaises(not_found, extract_post.extract_tags, fake_html)
        self.assertRaises(not_found, extract_post.extract_categories, fake_html)
        self.assertRaises(not_found, extract_post.extract_type, fake_html)
        self.assertRaises(not_found, extract_post.extract_status, fake_html)
        self.assertRaises(not_found, extract_post.extract_format, fake_html)
        self.assertRaises(not_found, extract_post.extract_word_count, fake_html)
        self.assertRaises(not_found, extract_post.extract_internal_links, fake_html)
        self.assertRaises(not_found, extract_post.extract_external_links, fake_html)
        self.assertRaises(not_found, extract_post.extract_vote_auth_code, fake_html)
        self.assertRaises(not_found, extract_post.extract_disqus_id, fake_html)

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