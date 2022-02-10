import random
from unittest.mock import AsyncMock, Mock, patch

from utils import (
    assert_is_valid_post,
    is_valid_edit_or_publish_date,
    is_valid_vote_or_comment_count,
)

from obscraper import _scrape
from obscraper._extract_post import is_valid_post_name

NUM_POSTS = 50


def test_core_api_produces_valid_posts_votes_and_comments(edit_dates):
    # sample N random names from the post list
    sample_names = random.sample(sorted(edit_dates.keys()), NUM_POSTS)
    sample_posts = _scrape.get_posts_by_names(sample_names)
    existing_posts = {
        name: post for name, post in sample_posts.items() if post is not None
    }
    for p in existing_posts.values():
        assert_is_valid_post(p)

    sample_numbers = {name: post.number for name, post in existing_posts.items()}
    sample_votes = _scrape.get_vote_counts(sample_numbers)
    for v in sample_votes.values():
        assert is_valid_vote_or_comment_count(v)

    sample_disqus_ids = {name: post.disqus_id for name, post in existing_posts.items()}
    sample_comments = _scrape.get_comment_counts(sample_disqus_ids)
    for c in sample_comments.values():
        assert is_valid_vote_or_comment_count(c)


def test_get_edit_dates_returns_expected_result(edit_dates):
    # Assert
    assert isinstance(edit_dates, dict)
    for name, date in edit_dates.items():
        assert is_valid_post_name(name)
        assert is_valid_edit_or_publish_date(date)


def test_clears_grab_post_cache():
    fake_post_numbers = {"/2020/06/fake-post": 12345}
    # Ideally I could mock the wrapped function inside _assemble.assemble_vote_count
    # but there is no nice way to do it
    with patch(
        "obscraper._download.download_vote_count", AsyncMock(side_effect=[123, 321])
    ) as mock_download:
        with patch("obscraper._tidy.tidy_vote_count", Mock(side_effect=lambda v: v)):
            _scrape.clear_cache()

            p1 = _scrape.get_vote_counts(fake_post_numbers)
            assert p1 == {"/2020/06/fake-post": 123}
            assert mock_download.call_count == 1

            p2 = _scrape.get_vote_counts(fake_post_numbers)
            assert p2 == {"/2020/06/fake-post": 123}
            assert mock_download.call_count == 1

            _scrape.clear_cache()
            p3 = _scrape.get_vote_counts(fake_post_numbers)
            assert p3 == {"/2020/06/fake-post": 321}
            assert mock_download.call_count == 2

            _scrape.clear_cache()
