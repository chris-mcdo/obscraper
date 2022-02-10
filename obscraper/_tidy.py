"""Produce a tidy object (or None) from a raw HTTP response."""

import json
import re

import bs4
import dateutil.parser

from . import _exceptions, _extract_post, _post


def tidy_post(response):
    """Tidy raw response from a post page.

    Parameters
    ----------
    response : httpx.Response
        Raw response from a post page.

    Returns
    -------
    obscraper.Post
        A Post object, extracted from the raw response.

    Raises
    ------
    obscraper.InvalidResponseError
        If the response does not look like an overcomingbias post.
    obscraper.AttributeNotFoundError
        If an obscraper.Post attribute could not be extracted from the
        response text.
    """
    raw_html = bs4.BeautifulSoup(response.text, "lxml")
    assert _extract_post.is_ob_post_html(raw_html), "HTML is not overcomingbias post."

    new_post = _post.Post(
        # URL and title
        name=_extract_post.extract_name(raw_html),
        # Metadata
        number=_extract_post.extract_number(raw_html),
        page_type=_extract_post.extract_page_type(raw_html),
        page_status=_extract_post.extract_page_status(raw_html),
        page_format=_extract_post.extract_page_format(raw_html),
        # Tags and categories
        tags=_extract_post.extract_tags(raw_html),
        categories=_extract_post.extract_categories(raw_html),
        # Title, author, date
        title=_extract_post.extract_title(raw_html),
        author=_extract_post.extract_author(raw_html),
        publish_date=_extract_post.extract_publish_date(raw_html),
        # Word count and links
        text_html=_extract_post.extract_text_html(raw_html),
        word_count=_extract_post.extract_word_count(raw_html),
        internal_links=_extract_post.extract_internal_links(raw_html),
        external_links=_extract_post.extract_external_links(raw_html),
        # Disqus ID string
        disqus_id=_extract_post.extract_disqus_id(raw_html),
    )
    return new_post


def tidy_vote_count(response):
    """Tidy raw response from the vote count API.

    Note that an exception is *not* raised if the response does not
    correspond to a real post. This is because the vote count API
    returns 0 (rather than an error message) for posts that do not
    exist.

    Parameters
    ----------
    response : httpx.Response
        Raw response from the vote count API.

    Returns
    -------
    int
        The vote count stated in the response.
    """
    assert response.text != "-1", "Invalid Vote Auth Code."

    raw_json = json.loads(response.text)
    html_soup = bs4.BeautifulSoup(raw_json["items"][0]["html"], "lxml")

    pattern = r"(Rating:\s*\+{0,1})(\d+)(\s*vote)"
    match = re.search(pattern, html_soup.text).group(2)

    votes = int(match)
    return votes


def tidy_comment_count(response):
    """Tidy raw response from the comment count API.

    Parameters
    ----------
    response : httpx.Response
        Raw response from the comment count API.

    Returns
    -------
    int
        The comment count stated in the response.

    Raises
    ------
    obscraper.InvalidResponseError
        If no comment count is found in the response.
    """
    pattern = r"(?<=displayCount\()(.*)(?=\))"
    match = re.search(pattern, response.text).group()
    raw_json = json.loads(match)

    if raw_json["counts"] == []:
        raise _exceptions.InvalidResponseError("Comment count not found.")

    comments = raw_json["counts"][0]["comments"]
    return comments


def tidy_edit_dates(response):
    """Tidy edit dates XML document.

    Parameters
    ----------
    response : httpx.Response
        Raw response from the post list XML page on the overcomingbias
        site.

    Returns
    -------
    Dict[str, datetime.datetime]
        Dictionary whose keys are post names and values are the last
        edit dates of each post as aware datetime.datetime objects.
    """
    xml_soup = bs4.BeautifulSoup(response.text, "lxml-xml")

    url_tags = xml_soup.find_all("loc")
    urls = [tag.string for tag in url_tags]
    names = [_extract_post.url_to_name(url) for url in urls]

    date_tags = xml_soup.find_all("lastmod")
    dates = [dateutil.parser.isoparse(tag.string) for tag in date_tags]

    return dict(zip(names, dates))


def tidy_vote_auth(response):
    """Extract the vote auth code from a post page."""
    raw_html = bs4.BeautifulSoup(response.text, "lxml")
    assert _extract_post.is_ob_post_html(raw_html), "HTML is not overcomingbias post."

    vote_auth = _extract_post.extract_vote_auth_code(raw_html)
    return vote_auth
