"""Extract meta-data from an overcomingbias blog post."""

import re

from . import utils, exceptions

# timezone of server generating post timestamps
OB_SERVER_TZ = 'US/Eastern'

def extract_url(post_html):
    """Extract the URL of the post.
    
    Args:
        post_html: BeautifulSoup object. HTML of an OB post.
        Can be truncated.

    Returns:
        String. URL of the post.
    """
    match = post_html.find(attrs={'class': 'st_sharethis'})
    raise_attribute_not_found_error_if_none(match, 'URL')
    return match['st_url']

def extract_name(post_html):
    """Extract the name of the post."""
    match = re.search(r'(?<=/)[^/]+(?=\.html$)', extract_url(post_html))
    raise_attribute_not_found_error_if_none(match, 'name')
    return match.group().removesuffix('.html')

def extract_title(post_html):
    """Extract the title of the post."""
    match = post_html.find(attrs = {'class': 'entry-title'})
    raise_attribute_not_found_error_if_none(match, 'title')
    return match.text

def extract_author(post_html):
    """Extract the post author's name."""
    match = post_html.find(attrs = {'class': 'url fn n'})
    raise_attribute_not_found_error_if_none(match, 'author')
    return match.text

def extract_publish_date(post_html):
    """Extract the date the post was published."""
    match = post_html.find(attrs = {'class': 'entry-date'})
    raise_attribute_not_found_error_if_none(match, 'publish date')
    messy_date = match.text
    return utils.tidy_date(messy_date, OB_SERVER_TZ)

def extract_number(post_html):
    return int(extract_meta_header(post_html)['post'][0])

def extract_tags(post_html):
    return extract_meta_header(post_html).get('tag', [])

def extract_categories(post_html):
    return extract_meta_header(post_html).get('category', [])

def extract_type(post_html):
    return extract_meta_header(post_html)['type'][0]

def extract_status(post_html):
    return extract_meta_header(post_html)['status'][0]

def extract_format(post_html):
    return extract_meta_header(post_html).get('format', [''])[0]

def extract_word_count(post_html):
    match = post_html.find(attrs = {'class': 'entry-content'})
    raise_attribute_not_found_error_if_none(match, 'word count')
    words_to_ignore = ['GD', 'Star', 'Ratingloading']
    return utils.count_words(match.text, words_to_ignore)

def extract_internal_links(post_html):
    """Extract hyperlinks (to other OB webpages) of an OB post from its HTML.
    
    Return:
        A dict consisting of hyperlinks to OB webpages, and how many times
        they were repeated (usually 1).
    """
    match = post_html.find(attrs = {'class': 'entry-content'})
    raise_attribute_not_found_error_if_none(match, 'internal links')

    all_links = [ tag['href'] for tag in match.find_all('a') ]
    int_links = [ link for link in all_links if is_ob_post_url(link) ]

    int_link_dict = {}
    for link in int_links:
        int_link_dict[link] = int_link_dict.get(link, 0) + 1
    
    return int_link_dict

def extract_external_links(post_html):
    """Extract hyperlinks (to non-OB webpages) of an OB post from its HTML.
    
    Returns:
        A dict consisting of hyperlinks to non-OB webpages, and how many times
        they were repeated (usually 1).
    """
    match = post_html.find(attrs = {'class': 'entry-content'})
    raise_attribute_not_found_error_if_none(match, 'external links')

    all_links = [tag['href'] for tag in match.find_all('a')]    
    ext_links = [link for link in all_links if not is_ob_post_url(link)]

    ext_link_dict = {}
    for link in ext_links:
        ext_link_dict[link] = ext_link_dict.get(link, 0) + 1
    
    return ext_link_dict

def extract_vote_auth_code(post_html):
    """Extract the vote authorisation code, or return None."""
    match = re.search(r'(gdsr_cnst_nonce\s*=\s*")(\w+)("\s*;)', str(post_html), re.MULTILINE)
    raise_attribute_not_found_error_if_none(match, 'vote auth code')
    return match.group(2)

def extract_disqus_id(post_html):
    """Extract the Disqus ID string."""
    match = post_html.find(attrs={'class': 'dsq-postid'})
    raise_attribute_not_found_error_if_none(match, 'Disqus ID')
    return post_html.find(attrs={'class': 'dsq-postid'})['data-dsqidentifier']

def extract_meta_header(post_html):
    """Extract metadata header from a post.
    
    Returns:
        Dictionary whose keys are attribute names and
        values are and lists of attribute values. 
        Some attributes (e.g. tags) have multiple values,
        others (e.g. post type and status) have only one.
        Some attributes (e.g. "hentry") have no values.
    """
    match = post_html.find(has_post_in_id)
    raise_attribute_not_found_error_if_none(match, 'metadata')
    raw_headers = match['class']
    headers = [header.split(sep='-', maxsplit=1) for header in raw_headers]
    keys = [header[0] for header in headers]
    values = [header[1] if len(header) == 2 else None for header in headers]
    header_dict = { k:[] for k in keys }
    for key, value in zip(keys, values):
        if value is not None: header_dict[key].append(value)
    return header_dict

def has_post_in_id(tag):
    """Check whether the id attribute of an html tag contains the word "post"."""
    return tag.has_attr('id') and bool(re.compile('^post-\d+$').search(tag['id']))

def is_ob_post_url(url):
    """Check whether a URL corresponds to an overcomingbias post."""
    return is_ob_post_long_url(url) or is_ob_post_short_url(url)

def is_ob_post_long_url(url):
    """Check whether a URL is a overcomingbias post long URL.
    
    A long URL is one which contains the "name" of the post, e.g.
    https://www.overcomingbias.com/2011/05/jobs-kill-big-time.html.
    """
    return re.search(r'^https{0,1}://www.overcomingbias.com/\d{4}/\d{2}/\S+\.html$', url) is not None    

def is_ob_post_short_url(url):
    """Check whether a URL is a overcomingbias post short URL.
    
    A short URL is one which contains the "number" of the post, e.g.
    https://www.overcomingbias.com/?p=26449.
    """
    return re.search(r'^https{0,1}://www.overcomingbias.com/\?p=\d+$', url) is not None

def is_ob_site_html(html):
    """Check if some HTML is from the overcomingbias site.
    
    Args:
        html: BeautifulSoup object. An HTML page, possibly from
        the overcomingbias site.
    """
    site_title = html.find(id='site-title')
    if site_title is not None:
        return 'www.overcomingbias.com' in site_title.a['href']
    else:
        return False

def is_ob_post_html(html):
    """Check if some HTML corresponds to an overcomingbias blog post.
    
    Args:
        html: BeautifulSoup object. An HTML page, possibly from
        the overcomingbias site.
    """
    if not is_ob_site_html(html):
        return False
    return "single-post" in html.body['class']

def raise_attribute_not_found_error_if_none(object, attribute_name):
    """Raise an AttributeNotFoundError if an object is None."""
    if object is None:
        raise exceptions.AttributeNotFoundError(f'{attribute_name} could not be extracted from post HTML')