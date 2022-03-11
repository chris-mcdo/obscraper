import datetime
import re

from obscraper import _post, _utils
from obscraper._extract_post import (
    is_valid_disqus_id,
    is_valid_post_long_url,
    is_valid_post_url,
)


def tidy_us_date(d):
    return _utils.tidy_date(d, "US/Eastern")


def assert_is_valid_post(test_post, votes=True, comments=True, edit_date=True):
    assert_post_has_standard_attributes(test_post)
    assert_post_standard_attributes_have_correct_types(test_post)
    assert_post_standard_attributes_have_valid_values(test_post)
    if votes:
        assert is_valid_vote_or_comment_count(test_post.votes)
    else:
        assert test_post.votes is None
    if comments:
        assert is_valid_vote_or_comment_count(test_post.comments)
    else:
        assert test_post.comments is None
    if edit_date:
        assert is_valid_edit_or_publish_date(test_post.edit_date)
    else:
        assert test_post.edit_date is None


def assert_post_has_standard_attributes(test_post):
    assert isinstance(test_post, _post.Post)
    for attr in [
        "url",
        "name",
        "title",
        "author",
        "publish_date",
        "number",
        "tags",
        "categories",
        "page_type",
        "page_status",
        "page_format",
        "text_html",
        "word_count",
        "internal_links",
        "external_links",
        "disqus_id",
    ]:
        assert hasattr(test_post, attr)


def assert_post_standard_attributes_have_correct_types(test_post):
    # str
    for attr in [
        "url",
        "name",
        "title",
        "author",
        "page_type",
        "page_status",
        "page_format",
        "text_html",
        "disqus_id",
    ]:
        assert isinstance(getattr(test_post, attr), str)
    # datetime.datetime
    assert isinstance(test_post.publish_date, datetime.datetime)
    # int
    assert isinstance(test_post.number, int)
    assert isinstance(test_post.word_count, int)
    # list
    assert isinstance(test_post.tags, list)
    assert isinstance(test_post.categories, list)
    assert isinstance(test_post.internal_links, list)
    assert isinstance(test_post.external_links, list)
    # list elements
    for tag in test_post.tags:
        assert isinstance(tag, str)
    for cat in test_post.categories:
        assert isinstance(cat, str)
    for url in test_post.internal_links:
        assert isinstance(url, str)
    for url in test_post.external_links:
        assert isinstance(url, str)


def assert_post_standard_attributes_have_valid_values(test_post):
    # URL and title
    assert is_valid_post_long_url(test_post.url)
    assert re.search(r"^/\d{4}/\d{2}/[a-z0-9-_%]+$", test_post.name) is not None
    # Metadata
    assert 9999 < test_post.number < 100000
    assert test_post.page_type == "post"
    assert test_post.page_status == "publish"
    assert test_post.page_format == "standard"
    # Tags and categories
    for tag in test_post.tags:
        assert re.search(r"^[a-z0-9-]+$", tag)
    for cat in test_post.categories:
        assert re.search(r"^[a-z0-9-]+$", cat)
    # Title, author, date
    assert test_post.title != ""
    assert re.search(r"^[A-Za-z0-9\. ]+$", test_post.author)
    assert is_valid_edit_or_publish_date(test_post.publish_date)
    # Word count and links
    assert test_post.plaintext != ""
    assert test_post.word_count > 2  # /2008/12/cryonics-is-cool, found via random test
    for url in test_post.internal_links:
        assert is_valid_post_url(url)
    for url in test_post.external_links:
        assert not is_valid_post_url(url)
    # Disqus ID string
    assert is_valid_disqus_id(test_post.disqus_id)


def is_valid_vote_or_comment_count(count):
    if isinstance(count, int) and 0 <= count < 1000:
        return True
    else:
        return False


def is_valid_edit_or_publish_date(date):
    """Assert a date is an aware datetime between the year 2000 and right now."""
    utc = datetime.timezone.utc
    year_2000 = datetime.datetime(2000, 1, 1, tzinfo=utc)
    now = datetime.datetime.now(utc)

    if _utils.is_aware_datetime(date) and year_2000 < date < now:
        return True
    else:
        return False
