"""obscraper: scrape posts from the overcomingbias blog."""
import logging

from ._exceptions import AttributeNotFoundError, InvalidResponseError
from ._extract_post import name_to_url, url_to_name
from ._post import Post
from ._scrape import (
    clear_cache,
    get_all_posts,
    get_comment_counts,
    get_edit_dates,
    get_post_by_name,
    get_post_by_url,
    get_posts_by_edit_date,
    get_posts_by_names,
    get_posts_by_urls,
    get_vote_counts,
)
from ._serialize import PostDecoder, PostEncoder

__all__ = [
    "Post",
    "get_posts_by_names",
    "get_vote_counts",
    "get_comment_counts",
    "get_edit_dates",
    "get_all_posts",
    "get_post_by_name",
    "get_post_by_url",
    "get_posts_by_urls",
    "get_posts_by_edit_date",
    "clear_cache",
    "url_to_name",
    "name_to_url",
    "PostEncoder",
    "PostDecoder",
    "InvalidResponseError",
    "AttributeNotFoundError",
    "OB_POST_URL_PATTERN",
]

# taken from _extract_post.url_to_name
OB_POST_URL_PATTERN = (
    r"(^https{0,1}://www.overcomingbias.com)"
    r"(/\d{4}/\d{2}/[a-z0-9-_%]+)"
    r"(\.html$)"
)
"""str : Regex pattern for "long" format overcomingbias URLs.

It consists of 3 capturing groups. The second group captures the post
name.
"""

# Logging config
logging.getLogger("obscraper").addHandler(logging.NullHandler())
