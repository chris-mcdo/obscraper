"""Grab full posts and their metadata from the web."""
import json
import re
import functools
import bs4
import cachetools.func

from . import extract_post, extract_dates, download, post, exceptions

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

    Parameter
    ---------
    url : str
        The URL of the post to grab.

    Returns
    -------
    post : post.Post
        The post corresponding to the input URL.

    Raises
    ------
    exceptions.InvalidResponseError
        If the URL returns a page that does not look like an
        overcomingbias post.
    exceptions.AttributeNotFoundError
        If a post.Post attribute could not be extracted from the
        downloaded page.
    """
    post_html = download.grab_html_soup(url)
    if not extract_post.is_ob_post_html(post_html):
        raise exceptions.InvalidResponseError(
            f'the document found at {url} was not an overcomingbias post')
    return post.create_post(post_html)


@cachetools.func.ttl_cache(maxsize=1000, ttl=POST_DATA_CACHE_TIMEOUT)
def grab_comments(disqus_id):
    """Download comment count of overcomingbias post.

    Parameter
    ---------
    disqus_id : str
        The Disqus ID string of the post.

    Returns
    -------
    count : post.Post
        The post corresponding to the input URL.

    Raises
    ------
    exceptions.InvalidResponseError
        If no comment count is found for the given Disqus ID.
    """
    params = {'1': disqus_id}
    response = download.http_post_request(DISQUS_URL, params=params)
    raw_json = json.loads(
        re.search(r'(?<=displayCount\()(.*)(?=\))', response.text).group())
    if raw_json['counts'] == []:
        raise exceptions.InvalidResponseError(
            f'no comment count was found for Disqus ID {disqus_id}')
    return raw_json['counts'][0]['comments']


@cachetools.func.ttl_cache(maxsize=1, ttl=EDIT_DATES_CACHE_TIMEOUT)
def grab_edit_dates():
    """Download list of post URLs and last edit dates.

    Returns
    -------
    edit_dates : Dict[str, datetime.datetime]
        Dictionary whose keys are post URLs and values are the last edit
        dates of each post as aware datetime.datetime objects.
    """
    xml = download.grab_xml_soup(POST_LIST_URL)
    urls = extract_dates.extract_urls(xml)
    dates = extract_dates.extract_edit_dates(xml)
    return dict(zip(urls, dates))


def _auth_cache(func):
    """Use a cached authentication code if possible."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except exceptions.InvalidAuthCodeError:
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
    vote_count : int
        Integer number of votes the corresponding post has received.

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

    response = download.http_post_request(
        GDSR_URL, params=params, headers=headers)

    if response.text == '-1':
        raise exceptions.InvalidAuthCodeError(
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
    vote_auth_code : str
        Authorisation code used to gain access to the vote count API.
    """
    post_html = download.grab_html_soup(VOTE_AUTH_UPDATE_URL)
    return extract_post.extract_vote_auth_code(post_html)


def vote_identifier(number):
    """String used to identify a post to the vote count API."""
    return f'atr.{number}'
