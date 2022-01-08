
from functools import wraps, cache
import json
import re
import bs4
from . import extract_post, extract_dates, download, post, exceptions

POST_LIST_URL = 'https://www.overcomingbias.com/post.xml'
GDSR_URL = 'https://www.overcomingbias.com/wp-content/plugins/gd-star-rating/ajax.php'
DISQUS_URL = 'https://overcoming-bias.disqus.com/count-data.js'
# URL used to update the vote auth code
VOTE_AUTH_UPDATE_URL = 'https://www.overcomingbias.com/2011/12/life-is-good.html'

def grab_post_by_url(url):
    """Download and create a post object from its URL.
    
    Expects (and therefore doesn't check for) a valid OB
    post URL. But will return an InvalidResponseError if
    the resulting HTML is not an OB post.

    Args:
        url: String. The URL of the post to grab.
    
    Returns:
        A Post object containing the post data. 
    """
    post_html = download.grab_html_soup(url)
    if not extract_post.is_ob_post_html(post_html):
        raise exceptions.InvalidResponseError(f'The document found at {url} was not an overcomingbias post')
    return post.create_post(post_html)

def grab_comments(disqus_id):
    """Download comment count of overcomingbias post."""
    params = {'1': disqus_id}
    response = download.http_post_request(DISQUS_URL, params=params)
    raw_json = json.loads(re.search(r'(?<=displayCount\()(.*)(?=\))', response.text).group())
    if raw_json['counts'] != []:
        return raw_json['counts'][0]['comments']
    else:
        raise exceptions.InvalidResponseError(f'no comment count was found for Disqus ID {disqus_id}')

def grab_edit_dates():
    """Grab list of post URLs and last edit dates.

    Returns:
        Dictionary. A dict whose keys are post URLs and values are the last edit
        dates of each post (stored as strings). 
    """
    xml = download.grab_xml_soup(POST_LIST_URL)
    urls = extract_dates.extract_urls(xml)
    dates = extract_dates.extract_edit_dates(xml)
    return {url: date for url, date in zip(urls, dates)}

def cache_auth(func):
    """Use a cached authentication code if possible."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except exceptions.InvalidAuthCodeError:
            vote_auth_code.cache_clear()
            return func(*args, **kwargs)
    return wrapper

@cache_auth
def grab_votes(number):
    """Download the number of votes given to an OB post.
    
    Raises an InvalidAuthCodeError if the vote auth code 
    returned by vote_auth_code() is invalid. Doesn't raise
    an error if the post number is not valid; the vote count
    API will return a valid result for invalid post numbers,
    so this function can't tell it apart.

    Args:
        number: Integer. The unique integer identifier of the post.
    
    Returns:
        Integer number of votes the corresponding post has
        received.
    """
    headers = {'x-requested-with': 'XMLHttpRequest'}
    params = {
        '_ajax_nonce': vote_auth_code(),
        'vote_type': 'cache',
        'vote_domain': 'a',
        'votes': vote_identifier(number)
    }
    
    response = download.http_post_request(GDSR_URL, params=params, headers=headers)

    if response.text == '-1':
        raise exceptions.InvalidAuthCodeError('Vote auth code is invalid or expired')

    raw_json = json.loads(response.text)
    html_soup = bs4.BeautifulSoup(raw_json['items'][0]['html'], 'lxml')
    votes = re.search(r'(Rating:\s*\+{0,1})(\d+)(\s*vote)', html_soup.text).group(2)
    return int(votes)

@cache
def vote_auth_code():
    """Authorisation code used to gain access to the vote count API.
    
    The code is a WordPress nonce ("number used once"). It is actually
    a string and not a number. They probably have a lifetime of 24 
    hours. Source: https://codex.wordpress.org/WordPress_Nonces. 
    """
    post_html = download.grab_html_soup(VOTE_AUTH_UPDATE_URL)
    return extract_post.extract_vote_auth_code(post_html)

def vote_identifier(number):
    """String used to identify a post to the vote count API."""
    return f'atr.{number}'