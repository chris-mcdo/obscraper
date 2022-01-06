"""Scrape data from an overcomingbias archive page."""

import math
import re
from . import extract_post, utils, grab

# Maximum number of pages to look through on a single run. 
MAX_PAGES = 1000
# timezone of server generating post timestamps
OB_SERVER_TZ = 'US/Eastern'

def extract_post_html_list(page_html):
    """Extract post content HTML for multiple posts."""
    return page_html.find_all(has_post_in_id)

def extract_post_html(page_html):
    """Extract post content HTML for a single post."""
    return extract_post_html_list(page_html)[0]

def has_post_in_id(tag):
    """Check whether the id attribute of an html tag contains the word "post"."""
    return tag.has_attr('id') and bool(re.compile('^post-\d+$').search(tag['id']))

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

def is_single_ob_post_html(html):
    """Check if some HTML correspondings to a full blog post page.
    
    Args:
        html: BeautifulSoup object. An HTML page, possibly from
        the overcomingbias site.
    """
    if not is_ob_site_html(html):
        return False
    return "single-post" in html.body['class']

def is_ob_page_html(html):
    """Check if some HTML correspondings to a full blog post page.
    
    Args:
        html: BeautifulSoup object. An HTML page, possibly from
        the overcomingbias site.
    """
    if not is_ob_site_html(html):
        return False
    return {'home', 'blog'} <= set(html.body['class'])

def is_ob_post_url(url):
    """Check whether a URL corresponds to an overcomingbias post."""
    return re.search(r'^https{0,1}://www.overcomingbias.com/(\d{4}/\d{2}/\S+\.html|\?p=\d+)$', url) is not None

def extract_publish_dates(page_html):
    messy_dates = page_html.find_all(attrs = {'class': 'entry-date'})
    return [utils.tidy_date(d.text, OB_SERVER_TZ) for d in messy_dates]

def has_post_moved(post_html):
    """Check if a post has moved from the overcomingbias site.
    
    Args:
        post_html: BeautifulSoup object. The HTML of an overcomingbias
        post.
    """
    return extract_post.extract_author(post_html) == "Eliezer Yudkowsky"

def is_post_truncated(post_html):
    """Determine if a page has been truncated.
    
    Checks if a page has been truncated by seeing if it has a
    "continue reading" link.
    """
    continue_reading_tag = post_html.find('a', attrs={'class': 'more-link'})
    return continue_reading_tag is not None
