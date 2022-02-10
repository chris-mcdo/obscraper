import datetime
from unittest.mock import AsyncMock, patch

import pytest
from utils import tidy_us_date

from obscraper import _exceptions, _scrape
from obscraper._extract_post import name_to_url


def now():
    return datetime.datetime.now(datetime.timezone.utc)


def days_from_now(n):
    return now() + n * datetime.timedelta(days=1)


@pytest.fixture
def mock_fetch_posts():
    """Return mock posts for 3 examples, and None otherwise."""
    fake_posts = {
        "/2006/11/introduction": "intro",
        "/2021/10/what-makes-stuff-rot": "rot",
        "/2014/07/limits-on-generality": "generality",
    }

    async def fetch_posts(names_dict):
        results = {}
        for label, name in names_dict.items():
            results[label] = fake_posts.get(name, None)

        return results

    return AsyncMock(side_effect=fetch_posts)


class TestGetPostsByNames:
    def test_returns_empty_dict_for_empty_list(self):
        names = []
        posts = _scrape.get_posts_by_names(names)
        assert posts == {}

    def test_raises_type_error_if_names_are_wrong_type(self):
        for names in [
            ["/2007/10/a-rational-argu", None],
            [3514, 8293],
        ]:
            with pytest.raises(TypeError):
                _scrape.get_posts_by_names(names)

    def test_raises_value_error_if_names_in_wrong_format(self):
        for names in [
            ["Not a name"],
            ["/"],
            ["/123/456/ok"],
            ["/post"],
            ["/page/20/post"],
            ["/archives"],
        ]:
            with pytest.raises(ValueError):
                _scrape.get_posts_by_names(names)


class TestGetPostByName:
    def test_raises_type_error_if_name_is_wrong_type(self):
        for name in [None, 35]:
            with pytest.raises(TypeError):
                _scrape.get_post_by_name(name)

    def test_raises_value_error_if_name_in_wrong_format(self):
        for name in [
            "Not a name",
            "/?p=12345",
            "/abc/de/fg.html",
            "/archives",
        ]:
            with pytest.raises(ValueError):
                _scrape.get_post_by_name(name)

    def test_raises_error_when_post_not_found(self, mock_fetch_posts):
        name = "/2021/10/not-a-real-post"
        with patch("obscraper._fetch.fetch_posts", mock_fetch_posts):
            with pytest.raises(_exceptions.InvalidResponseError):
                _scrape.get_post_by_name(name)
        assert mock_fetch_posts.call_count == 1

    def test_returns_valid_posts_for_valid_names(self, mock_fetch_posts):
        name = "/2021/10/what-makes-stuff-rot"
        with patch("obscraper._fetch.fetch_posts", mock_fetch_posts):
            fake_post = _scrape.get_post_by_name(name)
        assert mock_fetch_posts.call_count == 1
        assert fake_post == "rot"


class TestGetPostsByURLs:
    def test_returns_empty_dict_for_empty_list(self):
        urls = []
        posts = _scrape.get_posts_by_urls(urls)
        assert posts == {}

    def test_raises_type_error_if_urls_are_wrong_type(self):
        for urls in [
            ["https://www.overcomingbias.com/2021/10/what-makes-stuff-rot.html", None],
            [3514, 8293],
        ]:
            with pytest.raises(TypeError):
                _scrape.get_posts_by_urls(urls)

    def test_raises_value_error_if_urls_in_wrong_format(self):
        for urls in [
            ["Not a url"],
            ["https://www.overcomingbias.com/?p=12345"],
            ["https://www.overcomingbias.com/abc/de/fg.html"],
            ["https://www.overcomingbias.com/1234/56/ab"],
            ["https://www.overcomingbias.com/page/20/"],
            ["https://www.overcomingbias.com/archives"],
        ]:
            with pytest.raises(ValueError):
                _scrape.get_posts_by_urls(urls)

    def test_returns_valid_posts_for_valid_urls(self, mock_fetch_posts):
        urls = [
            "https://www.overcomingbias.com/2021/10/what-makes-stuff-rot.html",
            "https://www.overcomingbias.com/2015/08/not-a-real-post.html",
        ]
        with patch("obscraper._fetch.fetch_posts", mock_fetch_posts):
            posts = _scrape.get_posts_by_urls(urls)
        assert isinstance(posts, dict)
        assert len(posts) == 2
        assert posts[urls[0]] == "rot"
        assert posts[urls[1]] is None


class TestGetPostByURL:
    def test_raises_type_error_if_url_is_wrong_type(self):
        for url in [None, 35]:
            with pytest.raises(TypeError):
                _scrape.get_post_by_url(url)

    def test_raises_value_error_if_url_in_wrong_format(self):
        for url in [
            "Not a url",
            "https://www.overcomingbias.com/?p=12345",
            "https://www.overcomingbias.com/abc/de/fg.html",
            "https://www.overcomingbias.com/1234/56/ab",
            "https://www.overcomingbias.com/archives",
        ]:
            with pytest.raises(ValueError):
                _scrape.get_post_by_url(url)

    def test_raises_error_when_post_not_found(self):
        url = "https://www.overcomingbias.com/2021/10/not-a-real-post.html"
        with pytest.raises(_exceptions.InvalidResponseError):
            _scrape.get_post_by_url(url)

    def test_returns_valid_posts_for_valid_urls(self, mock_fetch_posts):
        url = "https://www.overcomingbias.com/2006/11/introduction.html"
        with patch("obscraper._fetch.fetch_posts", mock_fetch_posts):
            fake_post = _scrape.get_post_by_url(url)
        assert fake_post == "intro"


class TestGetPostsByEditDate:
    def test_raises_type_error_if_dates_are_wrong_type(self):
        # Naive datetime
        with pytest.raises(TypeError):
            _scrape.get_posts_by_edit_date(
                start_date=now(), end_date=datetime.datetime.now()
            )

        # String
        with pytest.raises(TypeError):
            _scrape.get_posts_by_edit_date(
                start_date=days_from_now(-5),
                end_date="hi",
            )

        # Int
        with pytest.raises(TypeError):
            _scrape.get_posts_by_edit_date(start_date=1, end_date=now())

    def test_raises_value_error_if_end_date_before_start_date(self):
        with pytest.raises(ValueError):
            _scrape.get_posts_by_edit_date(start_date=now(), end_date=days_from_now(-1))

    def test_returns_valid_results_for_valid_arguments(
        self, edit_dates, mock_fetch_posts
    ):
        with patch("obscraper._scrape.get_edit_dates", return_value=edit_dates):
            with patch("obscraper._fetch.fetch_posts", mock_fetch_posts):
                # Future dates return empty dict
                assert _scrape.get_posts_by_edit_date(now(), days_from_now(5)) == {}

                # Past dates
                start_date = days_from_now(-1200)
                end_date = days_from_now(-800)
                posts = _scrape.get_posts_by_edit_date(start_date, end_date)

                # Check all names in results are in valid range
                for name in posts.keys():
                    assert start_date < edit_dates[name] < end_date

                # Check all names in the date range are in results
                for name, date in edit_dates.items():
                    if start_date < date < end_date:
                        assert name in posts.keys()


def test_get_all_posts_works_for_fake_edit_list():
    edit_dates = {
        "/2006/11/introduction": tidy_us_date("November 22, 2006 6:17 am"),
        "/2007/10/a-rational-argu": tidy_us_date("October 5, 2007 2:31 pm"),
        "/2021/04/shoulda-listened-futures": tidy_us_date("July 2, 2021 9:15 am"),
    }
    with patch(
        "obscraper._assemble.assemble_edit_dates", AsyncMock(return_value=edit_dates)
    ) as mock_fetch_edit_dates:
        posts = _scrape.get_all_posts()

    assert mock_fetch_edit_dates.call_count >= 1
    assert len(posts) == 3
    assert posts.pop("/2007/10/a-rational-argu") is None
    for name, p in posts.items():
        assert p.edit_date == edit_dates[name]


class TestGetVoteCounts:
    def test_returns_empty_dict_for_empty_dict(self):
        urls = {}
        posts = _scrape.get_vote_counts(urls)
        assert posts == {}

    def test_raises_type_error_if_arguments_are_wrong_type(self):
        for post_numbers in [
            18402,
            {
                name_to_url("/2006/11/introduction"): 18402,
                12345: 45678,
            },
            {
                name_to_url("/2009/05/we-only-need-a-handshake"): 18423,
                name_to_url("/2021/04/shoulda-listened-futures"): "Rogue string",
            },
        ]:
            with pytest.raises(TypeError):
                _scrape.get_vote_counts(post_numbers)

    def test_raises_value_error_if_arguments_have_wrong_value(self):
        for post_numbers in [
            {"intro": 18402, "new": 4567},
            {
                name_to_url("/2009/05/we-only-need-a-handshake"): 18423,
                name_to_url("/2021/04/shoulda-listened-futures"): 123456,
            },
        ]:
            with pytest.raises(ValueError):
                _scrape.get_vote_counts(post_numbers)

    def test_returns_zero_for_invalid_numbers(self):
        numbers = {"not-a-real-post": 12345}
        votes = _scrape.get_vote_counts(numbers)
        for name in numbers.keys():
            assert votes[name] == 0


class TestGetCommentCounts:
    def test_returns_empty_dict_for_empty_dict(self):
        urls = {}
        posts = _scrape.get_comment_counts(urls)
        assert posts == {}

    def test_raises_type_error_if_arguments_are_wrong_type(self):
        for disqus_ids in [
            "18402 http://prod.ob.trike.com.au/2006/11/how-to-join.html",
            {
                name_to_url(
                    "/2006/11/introduction"
                ): "18402 http://prod.ob.trike.com.au/2006/11/how-to-join.html",
                name_to_url("/2007/03/the_very_worst_"): 18481,
            },
            {
                name_to_url(
                    "/2009/05/we-only-need-a-handshake"
                ): "18423 http://www.overcomingbias.com/?p=18423",
                35618: "32811 http://www.overcomingbias.com/?p=32811",
            },
        ]:
            with pytest.raises(TypeError):
                _scrape.get_comment_counts(disqus_ids)

    def test_raises_value_error_if_arguments_have_wrong_value(self):
        for disqus_ids in [
            {
                name_to_url(
                    "/2006/11/introduction"
                ): "18402 http://prod.ob.trike.com.au/2006/11/how-to-join.html",
                name_to_url(
                    "/2007/03/the_very_worst_"
                ): "18141 http://prod.ob.trike.com.au/?p=18141",
            },
            {name_to_url("/2006/11/introduction"): ""},
        ]:
            with pytest.raises(ValueError):
                _scrape.get_comment_counts(disqus_ids)

    def test_returns_none_for_invalid_numbers(self):
        disqus_ids = {
            name_to_url("/2007/03/the_very_worst_"): "12345"
            " http://prod.ob.trike.com.au/2007/03/the-very-worst-kind-of-bias.html",
            name_to_url("/2021/04/shoulda-listened-futures"): "65432"
            " http://www.overcomingbias.com/?p=65432",
        }
        comments = _scrape.get_comment_counts(disqus_ids)
        for url in disqus_ids.keys():
            assert comments[url] is None


class TestRaiseExceptionIfNumberHasIncorrectFormat:
    @pytest.mark.parametrize("number", [12345, 54321, 10000, 99999])
    def test_no_exception_raised_if_number_has_correct_format(self, number):
        try:
            _scrape.raise_exception_if_number_has_incorrect_format(number)
        except ValueError:
            pytest.fail("ValueError raised")
        except TypeError:
            pytest.fail("TypeError raised")

    @pytest.mark.parametrize("number", ["Hello", ["A", "List"], 32.591, [12345]])
    def test_type_error_raised_if_number_has_wrong_type(self, number):
        with pytest.raises(TypeError):
            _scrape.raise_exception_if_number_has_incorrect_format(number)

    @pytest.mark.parametrize("number", [1, 9999, 100000, -12345])
    def test_value_error_raised_if_number_is_not_5_digits(self, number):
        with pytest.raises(ValueError):
            _scrape.raise_exception_if_number_has_incorrect_format(number)
