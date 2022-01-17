
import unittest

import bs4

from obscraper import _download, _exceptions, _extract_post, _grab, _utils

TEST_POST_NUMBERS = [
    18402,  # first post
    18141,  # early post by another author
    18115,  # 2007 post with embedded image
    18423,  # just before Disqus API changes
    30613,  # old post with embedded video
    32811,  # just before Disqus API changes for 2nd time
    33014,  # post with embedded tweet
]
TEST_DISQUS_IDS = {
    18402: '18402 http://prod.ob.trike.com.au/2006/11/how-to-join.html',
    18141: '18141 http://prod.ob.trike.com.au/2007/03/the-very-worst-kind-of-bias.html',
    18115: '18115 http://prod.ob.trike.com.au/2007/04/as-good-as-it-gets.html',
    18423: '18423 http://www.overcomingbias.com/?p=18423',
    30613: '30613 http://www.overcomingbias.com/?p=30613',
    32811: '32811 http://www.overcomingbias.com/?p=32811',
    33014: '33014 https://www.overcomingbias.com/?p=33014',
}


class TestExtractFunctionsOnExamplePosts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.post_htmls = {
            number:
            _download.grab_html_soup(
                f'https://www.overcomingbias.com/?p={number}')
            for number in TEST_POST_NUMBERS
        }

    def test_extract_url_returns_correct_results_for_valid_htmls(self):
        url = self.function_to_get_attribute_by_number(
            _extract_post.extract_url)
        self.assertEqual(
            url(18402), 'https://www.overcomingbias.com/2006/11/introduction.html')
        self.assertEqual(
            url(18141), 'https://www.overcomingbias.com/2007/03/the_very_worst_.html')
        self.assertEqual(
            url(18115), 'https://www.overcomingbias.com/2007/04/as_good_as_it_g.html')
        self.assertEqual(url(
            18423), 'https://www.overcomingbias.com/2009/05/we-only-need-a-handshake.html')
        self.assertEqual(url(
            30613), 'https://www.overcomingbias.com/2013/11/me-on-rt-america-4pm-est-today.html')
        self.assertEqual(url(
            32811), 'https://www.overcomingbias.com/2021/04/shoulda-listened-futures.html')
        self.assertEqual(
            url(33014), 'https://www.overcomingbias.com/2021/12/we-dont-have-to-die.html')

    def test_extract_name_returns_correct_results_for_valid_htmls(self):
        name = self.function_to_get_attribute_by_number(
            _extract_post.extract_name)
        self.assertEqual(name(18402), 'introduction')
        self.assertEqual(name(18141), 'the_very_worst_')
        self.assertEqual(name(18115), 'as_good_as_it_g')
        self.assertEqual(name(18423), 'we-only-need-a-handshake')
        self.assertEqual(name(30613), 'me-on-rt-america-4pm-est-today')
        self.assertEqual(name(32811), 'shoulda-listened-futures')
        self.assertEqual(name(33014), 'we-dont-have-to-die')

    def test_extract_title_returns_correct_results_for_valid_htmls(self):
        title = self.function_to_get_attribute_by_number(
            _extract_post.extract_title)
        self.assertEqual(title(18402), 'How To Join')
        self.assertEqual(title(18141), 'The Very Worst Kind of Bias')
        self.assertEqual(title(18115), 'As Good As It Gets')
        self.assertEqual(title(18423), 'Just A Handshake')
        self.assertEqual(title(30613), 'Me on RT America Soon')
        self.assertEqual(title(32811), 'Shoulda-Listened Futures')
        self.assertEqual(title(33014), 'We Don’t Have To Die')

    def test_extract_author_returns_correct_results_for_valid_htmls(self):
        author = self.function_to_get_attribute_by_number(
            _extract_post.extract_author)
        self.assertEqual(author(18402), 'Robin Hanson')
        self.assertEqual(author(18141), 'David J. Balan')
        self.assertEqual(author(18115), 'Robin Hanson')
        self.assertEqual(author(18423), 'Robin Hanson')
        self.assertEqual(author(30613), 'Robin Hanson')
        self.assertEqual(author(32811), 'Robin Hanson')
        self.assertEqual(author(33014), 'Robin Hanson')

    def test_extract_publish_date_returns_correct_results_for_valid_htmls(self):
        publish_date = self.function_to_get_attribute_by_number(
            _extract_post.extract_publish_date)

        def tidy(d): return _utils.tidy_date(d, 'US/Eastern')
        self.assertEqual(publish_date(18402), tidy(
            'November 20, 2006 6:00 am'))
        self.assertEqual(publish_date(18141), tidy('March 26, 2007 8:53 am'))
        self.assertEqual(publish_date(18115), tidy('April 7, 2007 6:00 am'))
        self.assertEqual(publish_date(18423), tidy('May 26, 2009 2:00 pm'))
        self.assertEqual(publish_date(30613), tidy(
            'November 12, 2013 2:20 pm'))
        self.assertEqual(publish_date(32811), tidy('April 27, 2021 6:45 pm'))
        self.assertEqual(publish_date(33014), tidy(
            'December 16, 2021 6:15 pm'))

    def test_extract_number_returns_correct_results_for_valid_htmls(self):
        number = self.function_to_get_attribute_by_number(
            _extract_post.extract_number)
        self.assertEqual(number(18402), 18402)
        self.assertEqual(number(18141), 18141)
        self.assertEqual(number(18115), 18115)
        self.assertEqual(number(18423), 18423)
        self.assertEqual(number(30613), 30613)
        self.assertEqual(number(32811), 32811)
        self.assertEqual(number(33014), 33014)

    def test_extract_tags_returns_correct_results_for_valid_htmls(self):
        tags = self.function_to_get_attribute_by_number(
            _extract_post.extract_tags)
        self.assertEqual(tags(18402), ['meta'])
        self.assertEqual(tags(18141), ['morality', 'psychology'])
        self.assertEqual(tags(18115), ['standard-biases'])
        self.assertEqual(tags(18423), ['signaling', 'social-science'])
        self.assertEqual(tags(30613), ['personal', 'social-science'])
        self.assertEqual(
            tags(32811), ['academia', 'prediction-markets', 'project'])
        self.assertEqual(tags(33014), ['future', 'medicine'])

    def test_extract_categories_returns_correct_results_for_valid_htmls(self):
        categories = self.function_to_get_attribute_by_number(
            _extract_post.extract_categories)
        self.assertEqual(categories(18402), ['meta'])
        self.assertEqual(categories(18141), ['morality', 'psychology'])
        self.assertEqual(categories(18115), ['standard-biases'])
        self.assertEqual(categories(18423), ['signaling', 'social-science'])
        self.assertEqual(categories(30613), ['uncategorized'])
        self.assertEqual(categories(32811), ['uncategorized'])
        self.assertEqual(categories(33014), ['uncategorized'])

    def test_extract_type_returns_correct_results_for_valid_htmls(self):
        type = self.function_to_get_attribute_by_number(
            _extract_post.extract_page_type)
        for number in TEST_POST_NUMBERS:
            self.assertEqual(type(number), 'post')

    def test_extract_status_returns_correct_results_for_valid_htmls(self):
        status = self.function_to_get_attribute_by_number(
            _extract_post.extract_page_status)
        for number in TEST_POST_NUMBERS:
            self.assertEqual(status(number), 'publish')

    def test_extract_format_returns_correct_results_for_valid_htmls(self):
        format = self.function_to_get_attribute_by_number(
            _extract_post.extract_page_format)
        for number in TEST_POST_NUMBERS:
            self.assertEqual(format(number), 'standard')

    def test_extract_text_returns_correct_start_and_end_for_valid_htmls(self):
        def extract_text(post_html):
            text_html = _extract_post.extract_text_html(post_html)
            return _extract_post.convert_to_plaintext(text_html)
        text = self.function_to_get_attribute_by_number(extract_text)
        self.assertTrue(text(18402).endswith(
            'Copyright is retained by each author.'))
        self.assertTrue(text(18141).endswith(
            'such beliefs are unlikely to correspond to truth.'))
        self.assertTrue(text(18115).endswith('but definitely worth living.'))
        self.assertTrue(text(18423).endswith(
            'even when backed by such publications.'))
        self.assertTrue(text(30613).endswith('here is the 5 minute video:'))
        self.assertTrue(text(32811).endswith(
            'will never be directly evaluated.'))
        self.assertTrue(text(33014).endswith('pretty minor issue here.'))

    def test_extract_word_count_returns_correct_results_for_valid_htmls(self):
        words = self.function_to_get_attribute_by_number(
            _extract_post.extract_word_count)
        self.assertEqual(words(18402), 263)
        self.assertEqual(words(18141), 315)
        self.assertEqual(words(18115), 155)
        self.assertEqual(words(18423), 247)
        self.assertEqual(words(30613), 28)
        self.assertEqual(words(32811), 1205)
        self.assertEqual(words(33014), 1336)  # likely to change

    def test_extract_internal_links_returns_correct_results_for_valid_htmls(self):
        internal_links = self.function_to_get_attribute_by_number(
            _extract_post.extract_internal_links)
        self.assertEqual(internal_links(18402), {
            'http://www.overcomingbias.com/2006/12/contributors_be.html': 1,
            'http://www.overcomingbias.com/2007/02/moderate_modera.html': 1,
        })
        self.assertEqual(internal_links(18141), {})
        self.assertEqual(internal_links(18115), {})
        self.assertEqual(internal_links(18423), {})
        self.assertEqual(internal_links(30613), {})
        self.assertEqual(internal_links(32811), {})
        self.assertEqual(internal_links(33014), {
            'https://www.overcomingbias.com/2012/06/frozen-or-plastic-brain.html': 1,
            'https://www.overcomingbias.com/2010/07/modern-male-sati.html': 1,
            'https://www.overcomingbias.com/2010/07/space-ashes-vs-cryonics.html': 1,
            'https://www.overcomingbias.com/2020/01/how-to-not-die-soon.html': 2,
            'https://www.overcomingbias.com/2008/12/tyler-on-cryonics.html': 1,
        })

    def test_extract_external_links_returns_correct_results_for_valid_htmls(self):
        external_links = self.function_to_get_attribute_by_number(
            _extract_post.extract_external_links)
        self.assertEqual(external_links(18402), {
            'http://www.fhi.ox.ac.uk/': 1,
        })
        self.assertEqual(external_links(18141), {
            'http://www.solstice.us/russell/religionciv.html': 1,
            'http://www.davidbrin.com/addiction.html': 1,
        })
        self.assertEqual(external_links(18115), {
            '/wp-content/uploads/2007/04/asgoodasitgets_2.jpg': 1,
        })
        self.assertEqual(external_links(18423), {
            'http://dx.doi.org/10.1016/j.geb.2009.05.001': 1,
        })
        self.assertEqual(external_links(30613), {
            'http://rt.com/on-air/rt-america-air/': 1,
        })
        self.assertEqual(external_links(32811), {})
        # Skip 33014

    def test_extract_auth_code_returns_result_in_correct_format(self):
        code = self.function_to_get_attribute_by_number(
            _extract_post.extract_vote_auth_code)
        for number in TEST_POST_NUMBERS:
            c = code(number)
            self.assertIsInstance(c, str)
            self.assertRegex(c, r'^[a-z0-9]{10}$')

    @unittest.skip('Vote auth code sometimes differs - not sure why')
    def test_extract_auth_code_returns_same_result_for_each_post(self):
        code = self.function_to_get_attribute_by_number(
            _extract_post.extract_vote_auth_code)
        unique_codes = set([code(number) for number in TEST_POST_NUMBERS])
        self.assertEqual(len(unique_codes), 1)
        self.assertRegex(unique_codes.pop(), r'^[a-z0-9]{10}$')

    def test_extract_disqus_id_returns_correct_results_for_valid_htmls(self):
        disqus_id = self.function_to_get_attribute_by_number(
            _extract_post.extract_disqus_id)
        self.assertEqual(
            disqus_id(18402), '18402 http://prod.ob.trike.com.au/2006/11/how-to-join.html')
        self.assertEqual(disqus_id(
            18141), '18141 http://prod.ob.trike.com.au/2007/03/the-very-worst-kind-of-bias.html')
        self.assertEqual(disqus_id(
            18115), '18115 http://prod.ob.trike.com.au/2007/04/as-good-as-it-gets.html')
        self.assertEqual(disqus_id(18423),
                         '18423 http://www.overcomingbias.com/?p=18423')
        self.assertEqual(disqus_id(30613),
                         '30613 http://www.overcomingbias.com/?p=30613')
        self.assertEqual(disqus_id(32811),
                         '32811 http://www.overcomingbias.com/?p=32811')
        self.assertEqual(disqus_id(33014),
                         '33014 https://www.overcomingbias.com/?p=33014')

    def function_to_get_attribute_by_number(self, extract_func):
        def func(number):
            return extract_func(self.post_htmls[number])
        return func


class TestExtractFunctionsOnFakePost(unittest.TestCase):
    def test_extract_functions_raise_exception_for_invalid_html(self):
        fake_html = bs4.BeautifulSoup('Fake HTML', features='lxml')
        not_found = _exceptions.AttributeNotFoundError
        self.assertRaises(not_found, _extract_post.extract_url, fake_html)
        self.assertRaises(not_found, _extract_post.extract_name, fake_html)
        self.assertRaises(not_found, _extract_post.extract_title, fake_html)
        self.assertRaises(not_found, _extract_post.extract_author, fake_html)
        self.assertRaises(
            not_found, _extract_post.extract_publish_date, fake_html)
        self.assertRaises(not_found, _extract_post.extract_number, fake_html)
        self.assertRaises(not_found, _extract_post.extract_tags, fake_html)
        self.assertRaises(
            not_found, _extract_post.extract_categories, fake_html)
        self.assertRaises(
            not_found, _extract_post.extract_page_type, fake_html)
        self.assertRaises(
            not_found, _extract_post.extract_page_status, fake_html)
        self.assertRaises(
            not_found, _extract_post.extract_page_format, fake_html)
        self.assertRaises(
            not_found, _extract_post.extract_text_html, fake_html)
        self.assertRaises(
            not_found, _extract_post.extract_word_count, fake_html)
        self.assertRaises(
            not_found, _extract_post.extract_internal_links, fake_html)
        self.assertRaises(
            not_found, _extract_post.extract_external_links, fake_html)
        self.assertRaises(
            not_found, _extract_post.extract_vote_auth_code, fake_html)
        self.assertRaises(
            not_found, _extract_post.extract_disqus_id, fake_html)


class TestIsOBPostURL(unittest.TestCase):
    # The two accepted formats look like this
    # https://www.overcomingbias.com/?p=32980
    # https://www.overcomingbias.com/2021/10/what-makes-stuff-rot.html
    def test_accepts_all_ob_post_urls(self):
        is_url = _extract_post.is_valid_post_url
        edit_dates = _grab.grab_edit_dates()
        [self.assertTrue(is_url(url)) for url in edit_dates.keys()]

    def test_rejects_incorrectly_formatted_urls(self):
        is_url = _extract_post.is_valid_post_url
        self.assertFalse(is_url('https://www.example.com/'))
        self.assertFalse(is_url('https://www.overcomingbias.com/p=32980'))
        self.assertFalse(is_url('https://www.overcomingbias.com/p=32980a'))
        self.assertFalse(
            is_url('https://www.overcomingbias.com/what-makes-stuff-rot.html'))
        self.assertFalse(
            is_url('https://www.overcomingbias.com/202/10/what-makes-stuff-rot.html'))
        self.assertFalse(
            is_url('https://www.overcomingbias.com/2021/10/what-makes-stuff-rot'))
        self.assertFalse(
            is_url('www.overcomingbias.com/2021/10/what-makes-stuff-rot'))


class TestDetermineOriginOfHTMLFiles(unittest.TestCase):
    def test_is_page_from_origin_functions_work_with_ob_post(self):
        test_html = _download.grab_html_soup(
            'https://overcomingbias.com/?p=27739')
        self.assertTrue(_extract_post.is_ob_site_html(test_html))
        self.assertTrue(_extract_post.is_ob_post_html(test_html))

    def test_is_page_from_origin_functions_work_with_ob_page(self):
        test_html = _download.grab_html_soup(
            'https://www.overcomingbias.com/page/1')
        self.assertTrue(_extract_post.is_ob_site_html(test_html))
        self.assertFalse(_extract_post.is_ob_post_html(test_html))

    def test_is_page_from_origin_functions_work_with_ob_home_page(self):
        test_html = _download.grab_html_soup('https://www.overcomingbias.com/')
        self.assertTrue(_extract_post.is_ob_site_html(test_html))
        self.assertFalse(_extract_post.is_ob_post_html(test_html))

    def test_is_page_from_origin_functions_work_with_example_dot_com_page(self):
        test_html = _download.grab_html_soup('https://example.com/')
        self.assertFalse(_extract_post.is_ob_site_html(test_html))
        self.assertFalse(_extract_post.is_ob_post_html(test_html))


class TestIsValidDisqusID(unittest.TestCase):
    def test_returns_true_for_valid_ids(self):
        valid = _extract_post.is_valid_disqus_id
        self.assertTrue(
            valid('18402 http://prod.ob.trike.com.au/2006/11/how-to-join.html'))
        self.assertTrue(valid(
            '18141 http://prod.ob.trike.com.au/2007/03/the-very-worst-kind-of-bias.html'))
        self.assertTrue(valid('18423 http://www.overcomingbias.com/?p=18423'))
        self.assertTrue(valid('32811 http://www.overcomingbias.com/?p=32811'))
        self.assertTrue(valid('33014 https://www.overcomingbias.com/?p=33014'))

    def test_returns_false_for_invalid_ids(self):
        valid = _extract_post.is_valid_disqus_id
        self.assertFalse(valid(12345))
        self.assertFalse(
            valid(['33014 https://www.overcomingbias.com/?p=33014']))
        self.assertFalse(
            valid('18402 http://prod.ob.trike.com.au/how-to-join.html'))
        self.assertFalse(valid('18402 http://prod.ob.trike.com.au/?p=18402'))
        self.assertFalse(
            valid('18402 http://www.overcomingbias.com/2006/11/how-to-join.html'))
        self.assertFalse(
            valid('18402 https://www.overcomingbias.com/2006/11/how-to-join.html'))
        self.assertFalse(
            valid('how-to-join.html http://prod.ob.trike.com.au/2006/11/how-to-join.html'))
        self.assertFalse(valid('http://www.overcomingbias.com/?p=32811'))
        self.assertFalse(valid('18423 http://www.overcomingbias.com/?p=18424'))
        self.assertFalse(valid(
            'how-to-join.html https://www.overcomingbias.com/2006/11/how-to-join.html'))
