"""Grab full posts and their metadata from the web.

This interface is internal - implementation details may change.
"""
import json
import re
import functools
import bs4
import cachetools.func

from . import _download, _exceptions, _extract_dates, _extract_post, _post

POST_LIST_URL = 'https://www.overcomingbias.com/post.xml'
GDSR_URL = ('https://www.overcomingbias.com/'
            'wp-content/plugins/gd-star-rating/ajax.php')
DISQUS_URL = 'https://overcoming-bias.disqus.com/count-data.js'
# URL used to update the vote auth code
VOTE_AUTH_UPDATE_URL = ('https://www.overcomingbias.com/'
                        '2011/12/life-is-good.html')
# Cache timeouts
VOTE_AUTH_CODE_CACHE_TIMEOUT = 43200
POST_DATA_CACHE_TIMEOUT = 3600
EDIT_DATES_CACHE_TIMEOUT = 300


@cachetools.func.ttl_cache(maxsize=100, ttl=POST_DATA_CACHE_TIMEOUT)
def grab_post_by_url(url):
    """Download and create a post object from its URL.

    Parameters
    ---------
    url : str
        The URL of the post to grab.

    Returns
    -------
    obscraper.Post
        The post corresponding to the input URL.

    Raises
    ------
    exceptions.InvalidResponseError
        If the URL returns a page that does not look like an
        overcomingbias post.
    exceptions.AttributeNotFoundError
        If a obscraper.Post attribute could not be extracted from the
        downloaded page.
    """
    post_html = _download.grab_html_soup(url)
    if not _extract_post.is_ob_post_html(post_html):
        raise _exceptions.InvalidResponseError(
            f'the document found at {url} was not an overcomingbias post')
    return create_post(post_html)


@cachetools.func.ttl_cache(maxsize=1000, ttl=POST_DATA_CACHE_TIMEOUT)
def grab_comments(disqus_id):
    """Download comment count of overcomingbias post.

    Parameters
    ---------
    disqus_id : str
        The Disqus ID string of the post.

    Returns
    -------
    int
        The comment count corresponding to the input Disqus ID.

    Raises
    ------
    exceptions.InvalidResponseError
        If no comment count is found for the given Disqus ID.
    """
    params = {'1': disqus_id}
    response = _download.http_post_request(DISQUS_URL, params=params)
    raw_json = json.loads(
        re.search(r'(?<=displayCount\()(.*)(?=\))', response.text).group())
    if raw_json['counts'] == []:
        raise _exceptions.InvalidResponseError(
            f'no comment count was found for Disqus ID {disqus_id}')
    return raw_json['counts'][0]['comments']


@cachetools.func.ttl_cache(maxsize=1, ttl=EDIT_DATES_CACHE_TIMEOUT)
def grab_edit_dates():
    """Download list of post URLs and last edit dates.

    Returns
    -------
    Dict[str, datetime.datetime]
        Dictionary whose keys are post URLs and values are the last edit
        dates of each post as aware datetime.datetime objects.
    """
    xml = _download.grab_xml_soup(POST_LIST_URL)
    urls = _extract_dates.extract_urls(xml)
    dates = _extract_dates.extract_edit_dates(xml)
    return dict(zip(urls, dates))


def _auth_cache(func):
    """Use a cached authentication code if possible."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except _exceptions.InvalidAuthCodeError:
            vote_auth_code.cache_clear()
            return func(*args, **kwargs)
    return wrapper


@cachetools.func.ttl_cache(maxsize=1000, ttl=POST_DATA_CACHE_TIMEOUT)
@_auth_cache
def grab_votes(number):
    """Download the number of votes given to an OB post.

    Note that an exception is *not* raised if a `number` does not
    correspond to a real post. This is because the vote count API
    returns 0 (rather than an error message) for posts that do not
    exist.

    Parameters
    ----------
    number : int
        The unique integer identifier of the post.

    Returns
    -------
    int
        The vote count corresponding to the input post number.

    Raises
    ------
    exceptions.InvalidAuthCodeError
        If the vote auth code returned by `vote_auth_code` is invalid.
    """
    headers = {'x-requested-with': 'XMLHttpRequest'}
    params = {
        '_ajax_nonce': vote_auth_code(),
        'vote_type': 'cache',
        'vote_domain': 'a',
        'votes': vote_identifier(number)
    }

    response = _download.http_post_request(
        GDSR_URL, params=params, headers=headers)

    if response.text == '-1':
        raise _exceptions.InvalidAuthCodeError(
            'vote auth code is invalid or expired')

    raw_json = json.loads(response.text)
    html_soup = bs4.BeautifulSoup(raw_json['items'][0]['html'], 'lxml')
    votes = re.search(
        r'(Rating:\s*\+{0,1})(\d+)(\s*vote)', html_soup.text).group(2)
    return int(votes)


@cachetools.func.ttl_cache(maxsize=1, ttl=VOTE_AUTH_CODE_CACHE_TIMEOUT)
def vote_auth_code():
    """Authorisation code used to gain access to the vote count API.

    The code is a WordPress nonce ("number used once"). It is actually
    a string and not a number. They probably have a lifetime of 24
    hours. Source: https://codex.wordpress.org/WordPress_Nonces.

    Returns
    -------
    str
        Authorisation code used to gain access to the vote count API.
    """
    post_html = _download.grab_html_soup(VOTE_AUTH_UPDATE_URL)
    return _extract_post.extract_vote_auth_code(post_html)


def vote_identifier(number):
    """String used to identify a post to the vote count API."""
    return f'atr.{number}'


def create_post(post_html, votes=True, comments=True):
    """Populate a post object using its HTML.

    Initialises post with all attributes except `edit_date`, which must
    be attached afterwards.

    Parameters
    ----------
    post_html : bs4.BeautifulSoup
        Full HTML of an overcomingbias post page.
    votes : bool
        Whether to collect the vote count when creating the post.
    comments : bool
        Whether to collect the comment count when creating the post.

    Returns
    -------
    obscraper.Post
        Post initialised from the inputted HTML. Includes vote and
        comment counts (if the `vote` and `comment` flags are set to
        True), but does not `edit_date`.
    """
    new_post = _post.Post(
        # URL and title
        url=_extract_post.extract_url(post_html),
        name=_extract_post.extract_name(post_html),
        # Metadata
        number=_extract_post.extract_number(post_html),
        page_type=_extract_post.extract_page_type(post_html),
        page_status=_extract_post.extract_page_status(post_html),
        page_format=_extract_post.extract_page_format(post_html),
        # Tags and categories
        tags=_extract_post.extract_tags(post_html),
        categories=_extract_post.extract_categories(post_html),
        # Title, author, date
        title=_extract_post.extract_title(post_html),
        author=_extract_post.extract_author(post_html),
        publish_date=_extract_post.extract_publish_date(post_html),
        # Word count and links
        text_html=_extract_post.extract_text_html(post_html),
        word_count=_extract_post.extract_word_count(post_html),
        internal_links=_extract_post.extract_internal_links(post_html),
        external_links=_extract_post.extract_external_links(post_html),
        # Disqus ID string
        disqus_id=_extract_post.extract_disqus_id(post_html),
    )
    if votes:
        new_post.votes = grab_votes(new_post.number)
    if comments:
        new_post.comments = grab_comments(new_post.disqus_id)
    return new_post
