"""obscraper: scrape posts from the overcomingbias blog."""
from ._post import Post
from ._scrape import get_all_posts
from ._scrape import get_post_by_url
from ._scrape import get_posts_by_urls
from ._scrape import get_posts_by_edit_date
from ._scrape import get_votes
from ._scrape import get_comments
from ._scrape import clear_cache
from ._grab import grab_edit_dates
from ._serialize import PostEncoder
from ._serialize import PostDecoder
from ._exceptions import InvalidResponseError
from ._exceptions import InvalidAuthCodeError
from ._exceptions import AttributeNotFoundError

__all__ = [
    'Post',
    'get_all_posts',
    'get_post_by_url',
    'get_posts_by_urls',
    'get_posts_by_edit_date',
    'get_votes',
    'get_comments',
    'clear_cache',
    'grab_edit_dates',
    'PostEncoder',
    'PostDecoder',
    'InvalidResponseError',
    'InvalidAuthCodeError',
    'AttributeNotFoundError',
    'OB_POST_URL_PATTERN',
]


OB_POST_URL_PATTERN = (
    r'(^https{0,1}://www.overcomingbias.com)'
    r'(/\d{4}/\d{2}/[a-z0-9-_%]+)'
    r'(\.html$)')
"""str : Regex pattern for "long" format overcomingbias URLs.

It consists of 3 capturing groups. The second group captures the post
name.
"""
