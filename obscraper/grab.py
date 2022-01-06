
from functools import wraps, cache
import json
import re
import bs4
from . import extract_page, extract_post, extract_dates, download, post, exceptions

OB_PAGE_URL = 'https://www.overcomingbias.com/page/'
POST_LIST_URL = 'https://www.overcomingbias.com/post.xml'
GDSR_URL = 'https://www.overcomingbias.com/wp-content/plugins/gd-star-rating/ajax.php'
DISQUS_URL = 'https://overcoming-bias.disqus.com/count-data.js'
# URL used to update the vote auth code
VOTE_AUTH_UPDATE_URL = 'https://www.overcomingbias.com/2011/12/life-is-good.html'

def grab_post_by_url(url):
    """Download and create a post object from its URL.
    
    Args:
        url: String. The URL of the post to grab.
    
    Returns:
        A Post object containing the post data. 
    """
    if not extract_page.is_ob_post_url(url):
        raise ValueError(f'The URL {url} is in wrong format to be overcomingbias post')
    post_html = download.grab_html_soup(url)
    if not extract_page.is_ob_site_html(post_html):
        raise ValueError(f'The URL {url} corresponds to a LessWrong post')
    if not extract_page.is_single_ob_post_html(post_html):
        raise exceptions.InvalidResponseError(f'The document found at {url} was not an overcomingbias post')
    return post.create_post(post_html)

def grab_page(page):
    """Download a page given its page number.
    
    Raises an InvalidResponseError if the page is not found.

    Args:
        page: int. The page number of the archive page.

    Returns:
        BeautifulSoup object representing the page HTML.
    """
    if page == 0:
        raise ValueError('Use of page 0 is forbidden to avoid bugs')
    page_html = download.grab_html_soup(f'{OB_PAGE_URL}{page}')
    if not extract_page.is_ob_page_html(page_html):
        raise exceptions.InvalidResponseError(f'Page {page} was not found')
    return page_html

def grab_all_posts_on_page(number):
    """Get all posts on a given archive page.

    If the post is truncated on the archive page, the 
    full post is downloaded from the post HTML, except
    if the full post is no longer accessible on the
    overcomingbias site. I.e. if it has been moved to 
    LessWrong.

    Args:
        number: int. The page number of the archive page.

    Returns:
        List of post.Post objects.
    """
    page_html = grab_page(number)
    post_html_list = extract_page.extract_post_html_list(page_html)
    # Download full post HTML if post is truncated on archive page
    for i, post_html in enumerate(post_html_list):
        if extract_page.is_post_truncated(post_html) and not extract_page.has_post_moved(post_html):
            final_url = extract_post.extract_url(post_html)
            # Replace truncated post HTML with HTML from source.
            final_html = download.grab_html_soup(final_url)
            post_html_list[i] = extract_page.extract_post_html(final_html)
    return [post.create_post(post_html) for post_html in post_html_list]

def grab_comments(number):
    """Download the number of comments on an OB post from its number."""
    params = {'1': disqus_identifier(number)}
    response = download.http_post_request(DISQUS_URL, params=params)
    raw_json = json.loads(re.search(r'(?<=displayCount\()(.*)(?=\))', response.text).group())
    if raw_json['counts'] != []:
        return raw_json['counts'][0]['comments']
    else:
        raise exceptions.InvalidResponseError(f'No comment count was found for post {number}')

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

def grab_publish_dates(page):
    """Grab the publish dates of posts on a given page.
    
    Raises an InvalidResponseError if the page is not found.

    Returns:
        A list of publish dates as datetime.datetime objects.
    """
    html = grab_page(page)
    dates = extract_page.extract_publish_dates(html)
    return dates

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

def disqus_identifier(number):
    """String used to identify a post to the Disqus API."""
    return f'{number} http://www.overcomingbias.com/?p={number}'
