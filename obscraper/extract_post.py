"""Extract meta-data from an overcomingbias blog post."""

import re

from . import extract_page, utils

def extract_url(post_html):
    """Extract the URL of the post.
    
    Args:
        post_html: BeautifulSoup object. HTML of an OB post.
        Can be truncated.

    Returns:
        String. URL of the post.
    """
    return post_html.find(attrs={'class': 'st_sharethis'})['st_url']

def extract_name(post_html):
    """Extract the name of the post."""
    return re.search(r'(?<=/)([^/]+)(?=$)', extract_url(post_html)).group().removesuffix('.html')

def extract_title(post_html):
    """Extract the title of the post."""
    return post_html.find(attrs = {'class': 'entry-title'}).text

def extract_author(post_html):
    """Extract the post author's name."""
    return post_html.find(attrs = {'class': 'url fn n'}).text

def extract_publish_date(post_html):
    """Extract the date the post was published."""
    return extract_page.extract_publish_dates(post_html)[0]

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
    if extract_page.is_post_truncated(post_html):
        raise ValueError('cannot extract word count from a truncated post')

    words_to_ignore = ['GD', 'Star', 'Ratingloading...']
    return utils.count_words(post_html.find(attrs = {'class': 'entry-content'}).text, words_to_ignore)

def extract_internal_links(post_html):
    """Extract hyperlinks (to other OB webpages) of an OB post from its HTML.
    
    Return:
        A dict consisting of hyperlinks to OB webpages, and how many times
        they were repeated (usually 1).
    """
    if extract_page.is_post_truncated(post_html):
        raise ValueError('cannot extract hyperlinks from a truncated post')

    all_links = [ tag['href'] for tag in post_html.find(
        attrs = {'class': 'entry-content'}
        ).find_all('a') ]
    
    int_links = [ link for link in all_links if extract_page.is_ob_post_url(link) ]

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
    if extract_page.is_post_truncated(post_html):
        raise ValueError('cannot extract hyperlinks from a truncated post')

    all_links = [ tag['href'] for tag in post_html.find(
        attrs = {'class': 'entry-content'}
        ).find_all('a') ]
    
    ext_links = [ link for link in all_links if not extract_page.is_ob_post_url(link) ]
    ext_link_dict = {}
    for link in ext_links:
        ext_link_dict[link] = ext_link_dict.get(link, 0) + 1
    
    return ext_link_dict

def extract_meta_header(post_html):
    """Extract metadata header from a post."""
    if extract_page.has_post_in_id(post_html):
        raw_headers = post_html['class']
    else:
        raw_headers = post_html.find(extract_page.has_post_in_id)['class']
    headers = [header.split(sep='-', maxsplit=1) for header in raw_headers]
    keys = [header[0] for header in headers]
    values = [header[1] if len(header) == 2 else None for header in headers]
    header_dict = { k:[] for k in keys }
    for key, value in zip(keys, values):
        if value is not None: header_dict[key].append(value)
    return header_dict

def extract_vote_auth_code(page_html):
    """Extract the vote authorisation code, or return None."""
    match = re.search(r'(gdsr_cnst_nonce\s*=\s*")(\w+)("\s*;)', str(page_html), re.MULTILINE)
    return match.group(2) if match is not None else None

