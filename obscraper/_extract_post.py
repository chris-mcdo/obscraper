"""Extract meta-data from an overcomingbias blog post.

This interface is internal - implementation details may change.
"""

import re
import copy

import bs4

from . import _exceptions, _utils

OB_SERVER_TZ = 'US/Eastern'
# timezone of server generating post timestamps
DISQUS_URL_PATTERN = (
    r'^(\d{5})\ '
    r'(?:http://prod.ob.trike.com.au/\d{4}/\d{2}/\S+\.html$|'
    r'http://www.overcomingbias.com/\?p=\1|'
    r'https://www.overcomingbias.com/\?p=\1)$')


def extract_url(post_html):
    """Extract the URL of the post.

    Parameters
    ---------
    post_html : bs4.BeautifulSoup
        Full HTML of an overcomingbias post page.

    Returns
    -------
    url : str
        URL of the post.
    """
    match = post_html.find(attrs={'class': 'st_sharethis'})
    raise_attribute_not_found_error_if_none(match, 'URL')
    return match['st_url']


def extract_name(post_html):
    """Extract the name of the post.

    Parameters
    ---------
    post_html : bs4.BeautifulSoup
        Full HTML of an overcomingbias post page.

    Returns
    -------
    name : str
        Name of the post.
    """
    match = re.search(r'(?<=/)[^/]+(?=\.html$)', extract_url(post_html))
    raise_attribute_not_found_error_if_none(match, 'name')
    return match.group()


def extract_title(post_html):
    """Extract the title of the post.

    Parameters
    ---------
    post_html : bs4.BeautifulSoup
        Full HTML of an overcomingbias post page.

    Returns
    -------
    title : str
        Title of the post.
    """
    match = post_html.find(attrs={'class': 'entry-title'})
    raise_attribute_not_found_error_if_none(match, 'title')
    return match.text


def extract_author(post_html):
    """Extract the post author's name.

    Parameters
    ---------
    post_html : bs4.BeautifulSoup
        Full HTML of an overcomingbias post page.

    Returns
    -------
    author : str
        Author of the post.
    """
    match = post_html.find(attrs={'class': 'url fn n'})
    raise_attribute_not_found_error_if_none(match, 'author')
    return match.text


def extract_publish_date(post_html):
    """Extract the date the post was published.

    Parameters
    ---------
    post_html : bs4.BeautifulSoup
        Full HTML of an overcomingbias post page.

    Returns
    -------
    date : datetime.datetime
        When the post was first published. An aware datetime object.
    """
    match = post_html.find(attrs={'class': 'entry-date'})
    raise_attribute_not_found_error_if_none(match, 'publish date')
    messy_date = match.text
    return _utils.tidy_date(messy_date, OB_SERVER_TZ)


def extract_number(post_html):
    """Extract the unique integer identifier of the post.

    Parameters
    ---------
    post_html : bs4.BeautifulSoup
        Full HTML of an overcomingbias post page.

    Returns
    -------
    number : int
        Unique integer identifier of the post.
    """
    return int(extract_meta_header(post_html)['post'][0])


def extract_tags(post_html):
    """Extract post tags.

    Parameters
    ---------
    post_html : bs4.BeautifulSoup
        Full HTML of an overcomingbias post page.

    Returns
    -------
    tags : List[str]
        List of tags associated with the post.
    """
    return extract_meta_header(post_html).get('tag', [])


def extract_categories(post_html):
    """Extract post categories.

    Parameters
    ---------
    post_html : bs4.BeautifulSoup
        Full HTML of an overcomingbias post page.

    Returns
    -------
    categories : List[str]
        List of categories associated with the post.
    """
    return extract_meta_header(post_html).get('category', [])


def extract_page_type(post_html):
    """Extract page type.

    Parameters
    ---------
    post_html : bs4.BeautifulSoup
        Full HTML of an overcomingbias post page.

    Returns
    -------
    page_type : str
        Page type, normally 'post'. I don't know its definition.
    """
    return extract_meta_header(post_html)['type'][0]


def extract_page_status(post_html):
    """Extract page status.

    Parameters
    ---------
    post_html : bs4.BeautifulSoup
        Full HTML of an overcomingbias post page.

    Returns
    -------
    page_status : str
        Page status, normally 'publish'. I don't know its definition.
    """
    return extract_meta_header(post_html)['status'][0]


def extract_page_format(post_html):
    """Extract page format.

    Parameters
    ---------
    post_html : bs4.BeautifulSoup
        Full HTML of an overcomingbias post page.

    Returns
    -------
    page_format : str
        Page format, normally 'standard'. I don't know its definition.
    """
    return extract_meta_header(post_html).get('format', [''])[0]


def extract_text_html(post_html):
    """Extract lightly edited HTML of the post text.

    Parameters
    ---------
    post_html : bs4.BeautifulSoup
        Full HTML of an overcomingbias post page.

    Returns
    -------
    text_html : str
        Post text HTML, lightly edited.
    """
    match = post_html.find(attrs={'class': 'entry-content'})
    raise_attribute_not_found_error_if_none(match, 'text')
    # don't make changes to the original object
    match_copy = copy.copy(match)
    match_copy.find(attrs={'class': 'gdsrcacheloader'}).decompose()
    return str(match_copy)


def extract_word_count(post_html):
    """Extract post word count.

    Parameters
    ---------
    post_html : bs4.BeautifulSoup
        Full HTML of an overcomingbias post page.

    Returns
    -------
    word_count : int
        The number of words in the body of the post.
    """
    text_html = extract_text_html(post_html)
    text = convert_to_plaintext(text_html)
    return _utils.count_words(text)


def extract_all_links(post_html):
    """Extract all hyperlinks in the body of a post.

    Parameters
    ---------
    post_html : bs4.BeautifulSoup
        Full HTML of an overcomingbias post page.

    Returns
    -------
    all_links : List[str]
        A list of hyperlinks found in the body of the post.
    """
    match = post_html.find(attrs={'class': 'entry-content'})
    raise_attribute_not_found_error_if_none(match, 'links')

    link_tags = [tag for tag in match.find_all('a') if tag.has_attr('href')]
    all_links = [tag['href'] for tag in link_tags]
    return all_links


def extract_internal_links(post_html):
    """Extract links to other overcomingbias posts.

    Parameters
    ---------
    post_html : bs4.BeautifulSoup
        Full HTML of an overcomingbias post page.

    Returns
    -------
    internal_links : Dict[str, int]
        A dictionary whose keys record links to OB webpages within the
        post, and whose values record how many times each link is
        repeated (usually 1).
    """
    all_links = extract_all_links(post_html)
    int_links = [link for link in all_links if is_valid_post_url(link)]

    int_link_dict = {}
    for link in int_links:
        int_link_dict[link] = int_link_dict.get(link, 0) + 1

    return int_link_dict


def extract_external_links(post_html):
    """Extract links to other (non- OB post) webpages.

    Parameters
    ---------
    post_html : bs4.BeautifulSoup
        Full HTML of an overcomingbias post page.

    Returns
    -------
    internal_links : Dict[str, int]
        A dictionary whose keys record links to other webpages within
        the post, and whose values record how many times each link is
        repeated (usually 1).
    """
    all_links = extract_all_links(post_html)
    ext_links = [link for link in all_links if not is_valid_post_url(link)]

    ext_link_dict = {}
    for link in ext_links:
        ext_link_dict[link] = ext_link_dict.get(link, 0) + 1

    return ext_link_dict


def extract_vote_auth_code(post_html):
    """Extract the vote authorisation code, or return None.

    Parameters
    ---------
    post_html : bs4.BeautifulSoup
        Full HTML of an overcomingbias post page.

    Returns
    -------
    vote_auth_code : str
        Authorisation code used to gain access to the vote count API.
    """
    match = re.search(r'(gdsr_cnst_nonce\s*=\s*")(\w+)("\s*;)',
                      str(post_html), re.MULTILINE)
    raise_attribute_not_found_error_if_none(match, 'vote auth code')
    return match.group(2)


def extract_disqus_id(post_html):
    """Extract the Disqus ID string.

    Parameters
    ---------
    post_html : bs4.BeautifulSoup
        Full HTML of an overcomingbias post page.

    Returns
    -------
    disqus_id : str
        String ID used to identify the post to the Disqus API.
    """
    match = post_html.find(attrs={'class': 'dsq-postid'})
    raise_attribute_not_found_error_if_none(match, 'Disqus ID')
    return post_html.find(attrs={'class': 'dsq-postid'})['data-dsqidentifier']


def extract_meta_header(post_html):
    """Extract metadata header from a post."""
    match = post_html.find(has_post_in_id)
    raise_attribute_not_found_error_if_none(match, 'metadata')
    raw_headers = match['class']
    headers = [header.split(sep='-', maxsplit=1) for header in raw_headers]
    keys = [header[0] for header in headers]
    values = [header[1] if len(header) == 2 else None for header in headers]
    header_dict = {k: [] for k in keys}
    for key, value in zip(keys, values):
        if value is not None:
            header_dict[key].append(value)
    return header_dict


def convert_to_plaintext(text_html):
    """Convert post text from HTML to plaintext format.

    Parameters
    ---------
    text_html : str
        Post text HTML as given by `extract_text_html`.

    Returns
    -------
    text : str
        Full text of post as plaintext. Leading and trailing whitespace
        and some special characters are removed.
    """
    html = bs4.BeautifulSoup(text_html, 'lxml')
    text = html.text.replace('\xa0', ' ').strip()
    return text


def has_post_in_id(tag):
    """Check whether id attribute of html tag contains "post"."""
    if not tag.has_attr('id'):
        return False
    return bool(re.compile(r'^post-\d+$').search(tag['id']))


def is_valid_post_url(url):
    """Check whether a URL could belong to an overcomingbias post.

    Parameters
    ---------
    url : str
        A URL.

    Returns
    -------
    is_valid_url : bool
        True if the URL is a valid overcomingbias post URL, and False
        otherwise.
    """
    return is_valid_post_long_url(url) or is_valid_post_short_url(url)


def is_valid_post_long_url(url):
    """Check whether a URL is a valid "long" post URL.

    A long URL is one which contains the "name" of the post, e.g.
    https://www.overcomingbias.com/2011/05/jobs-kill-big-time.html.

    Parameters
    ---------
    url : str
        A URL.

    Returns
    -------
    is_valid_url : bool
        True if the URL is a valid overcomingbias post long URL, and
        False otherwise.
    """
    pattern = r'^https{0,1}://www.overcomingbias.com/\d{4}/\d{2}/\S+\.html$'
    return re.search(pattern, url) is not None


def is_valid_post_short_url(url):
    """Check whether a URL is a valid "short" post URL.

    A short URL is one which contains the "number" of the post, e.g.
    https://www.overcomingbias.com/?p=26449.

    Parameters
    ---------
    url : str
        A URL.

    Returns
    -------
    is_valid_url : bool
        True if the URL is a valid overcomingbias post short URL, and
        False otherwise.
    """
    pattern = r'^https{0,1}://www.overcomingbias.com/\?p=\d+$'
    return re.search(pattern, url) is not None


def is_ob_site_html(html):
    """Check if some HTML looks like it is from the overcomingbias site.

    Parameters
    ---------
    html : bs4.BeautifulSoup
        An HTML page, possibly from the overcomingbias site.

    Returns
    -------
    is_ob_site_html : bool
        True if the input HTML "looks like" it is from the
        overcomingbias site, and False otherwise.
    """
    site_title = html.find(id='site-title')
    if site_title is not None:
        return 'www.overcomingbias.com' in site_title.a['href']
    return False


def is_ob_post_html(html):
    """Check if some HTML looks like an overcomingbias blog post.

    Parameters
    ---------
    html : bs4.BeautifulSoup
        An HTML page, possibly from the overcomingbias site.

    Returns
    -------
    is_ob_post_html : bool
        True if the input HTML "looks like" an overcomingbias blog post,
        and False otherwise.
    """
    if not is_ob_site_html(html):
        return False
    return "single-post" in html.body['class']


def is_valid_disqus_id(disqus_id):
    """Check whether a string is a valid Disqus ID string.

    Parameters
    ---------
    disqus_id : str
        A possibly valid Disqus ID string.

    Returns
    -------
    is_valid_disqus_id : bool
        True if the input string is a valid Disqus ID string, and False
        otherwise.
    """
    if not isinstance(disqus_id, str):
        return False
    return re.compile(DISQUS_URL_PATTERN).search(disqus_id) is not None


def raise_attribute_not_found_error_if_none(obj, attribute_name):
    """Raise an AttributeNotFoundError if an object is None."""
    if obj is None:
        raise _exceptions.AttributeNotFoundError(
            f'{attribute_name} could not be extracted from post HTML')
