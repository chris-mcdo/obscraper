import bs4
import pytest

from obscraper import _exceptions, _extract_post


def test_extract_functions_raise_exception_for_invalid_html():
    fake_html = bs4.BeautifulSoup("Fake HTML", "lxml")
    not_found = _exceptions.AttributeNotFoundError
    pytest.raises(not_found, _extract_post.extract_url, fake_html)
    pytest.raises(not_found, _extract_post.extract_name, fake_html)
    pytest.raises(not_found, _extract_post.extract_title, fake_html)
    pytest.raises(not_found, _extract_post.extract_author, fake_html)
    pytest.raises(not_found, _extract_post.extract_publish_date, fake_html)
    pytest.raises(not_found, _extract_post.extract_number, fake_html)
    pytest.raises(not_found, _extract_post.extract_tags, fake_html)
    pytest.raises(not_found, _extract_post.extract_categories, fake_html)
    pytest.raises(not_found, _extract_post.extract_page_type, fake_html)
    pytest.raises(not_found, _extract_post.extract_page_status, fake_html)
    pytest.raises(not_found, _extract_post.extract_page_format, fake_html)
    pytest.raises(not_found, _extract_post.extract_text_html, fake_html)
    pytest.raises(not_found, _extract_post.extract_word_count, fake_html)
    pytest.raises(not_found, _extract_post.extract_internal_links, fake_html)
    pytest.raises(not_found, _extract_post.extract_external_links, fake_html)
    pytest.raises(not_found, _extract_post.extract_vote_auth_code, fake_html)
    pytest.raises(not_found, _extract_post.extract_disqus_id, fake_html)


class TestIsOBPostName:
    def test_accepts_all_ob_post_names(self, edit_dates):
        for name in edit_dates.keys():
            assert _extract_post.is_valid_post_name(name)

    def test_rejects_incorrectly_formatted_names(self):
        is_name = _extract_post.is_valid_post_name
        assert not is_name("2022/20/without-first-slash")
        assert not is_name("/1234/56/")
        assert not is_name("/2020/02/named.html")


class TestIsOBPostURL:
    # The two accepted formats look like this
    # https://www.overcomingbias.com/?p=32980
    # https://www.overcomingbias.com/2021/10/what-makes-stuff-rot.html
    def test_accepts_all_ob_post_urls(self, edit_dates):
        is_url = _extract_post.is_valid_post_url
        for name in edit_dates.keys():
            url = _extract_post.name_to_url(name)
            assert is_url(url)

    def test_rejects_incorrectly_formatted_urls(self):
        is_url = _extract_post.is_valid_post_url
        assert not is_url("https://www.example.com/")
        assert not is_url("https://www.overcomingbias.com/p=32980")
        assert not is_url("https://www.overcomingbias.com/p=32980a")
        assert not is_url("https://www.overcomingbias.com/what-makes-stuff-rot.html")
        assert not is_url(
            "https://www.overcomingbias.com/202/10/what-makes-stuff-rot.html"
        )
        assert not is_url("https://www.overcomingbias.com/2021/10/what-makes-stuff-rot")
        assert not is_url("www.overcomingbias.com/2021/10/what-makes-stuff-rot")


class TestDetermineOriginOfHTMLFiles:
    def test_is_page_from_origin_functions_work_with_ob_post(self, http_client):
        test_html = self.grab_page(
            http_client, "https://www.overcomingbias.com/2006/11/introduction.html"
        )
        assert _extract_post.is_ob_site_html(test_html)
        assert _extract_post.is_ob_post_html(test_html)

    def test_is_page_from_origin_functions_work_with_ob_page(self, http_client):
        test_html = self.grab_page(http_client, "https://www.overcomingbias.com/page/1")
        assert _extract_post.is_ob_site_html(test_html)
        assert not _extract_post.is_ob_post_html(test_html)

    def test_is_page_from_origin_functions_work_with_ob_home_page(self, http_client):
        test_html = self.grab_page(http_client, "https://www.overcomingbias.com/")
        assert _extract_post.is_ob_site_html(test_html)
        assert not _extract_post.is_ob_post_html(test_html)

    def test_is_page_from_origin_functions_work_with_example(self, http_client):
        test_html = self.grab_page(http_client, "https://www.example.com/")
        assert not _extract_post.is_ob_site_html(test_html)
        assert not _extract_post.is_ob_post_html(test_html)

    def grab_page(self, client, url):
        page = client.get(url)
        return bs4.BeautifulSoup(page.text, "lxml")


class TestIsValidDisqusID:
    def test_returns_true_for_valid_ids(self):
        valid = _extract_post.is_valid_disqus_id
        assert valid("18402 http://prod.ob.trike.com.au/2006/11/how-to-join.html")
        assert valid(
            "18141"
            " http://prod.ob.trike.com.au/2007/03/the-very-worst-kind-of-bias.html"
        )
        assert valid("18423 http://www.overcomingbias.com/?p=18423")
        assert valid("32811 http://www.overcomingbias.com/?p=32811")
        assert valid("33014 https://www.overcomingbias.com/?p=33014")

    def test_returns_false_for_invalid_ids(self):
        valid = _extract_post.is_valid_disqus_id
        assert not valid(12345)
        assert not valid(["33014 https://www.overcomingbias.com/?p=33014"])
        assert not valid("18402 http://prod.ob.trike.com.au/how-to-join.html")
        assert not valid("18402 http://prod.ob.trike.com.au/?p=18402")
        assert not valid("18402 http://www.overcomingbias.com/2006/11/how-to-join.html")
        assert not valid(
            "18402 https://www.overcomingbias.com/2006/11/how-to-join.html"
        )
        assert not valid(
            "how-to-join.html http://prod.ob.trike.com.au/2006/11/how-to-join.html"
        )
        assert not valid("http://www.overcomingbias.com/?p=32811")
        assert not valid("18423 http://www.overcomingbias.com/?p=18424")
        assert not valid(
            "how-to-join.html https://www.overcomingbias.com/2006/11/how-to-join.html"
        )


class TestConvertToPlaintext:
    def test_removes_correct_characters(self):
        example_string = (
            "<p> Remove this   but not  this’.\n"
            "And clear trailing whitespace...   </p>"
        )
        result = _extract_post.convert_to_plaintext(example_string)
        assert result == "Remove this but not this’.\nAnd clear trailing whitespace..."
