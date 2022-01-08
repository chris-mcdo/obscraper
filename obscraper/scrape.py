"""Get a list of posts by publish date or URL."""

import math
import datetime

from . import grab, extract_post, exceptions

def get_posts_by_url(urls):
    """Get list of posts identified by their URLs.
    
    If one of the URLs is in an incorrect format, an exception is
    raised. If a post is not found (i.e. an InvalidResponseError 
    occurs), None is returned for that particular post.

    Args:
        urls: List (String). A list of post URLs to scrape data for.

    Returns:
        urls: List (String). A list of post URLs to scrape data for.
    """
    for url in urls:
        if not isinstance(url, str):
            raise TypeError(f'expected URL to be string, got {url}')
        if not extract_post.is_ob_post_url(url):
            raise ValueError(f'expected URL to be OB post URL, got {url}')
    posts = []
    for url in urls:
        try:
            posts.append(grab.grab_post_by_url(url))
        except (exceptions.AttributeNotFoundError, exceptions.InvalidResponseError):
            posts.append(None)
    return attach_edit_dates(posts)

def get_votes(post_numbers):
    """Get vote counts for some posts.
    
    If one of the numbers is in an incorrect format, an exception is
    raised. Unlike other functions, get_votes returns 0 (rather than
    None) when a post is not found. This is because it is not possible
    to determine whether a post exists or not from the vote count API;
    it will just return 0 in this case. 

    Args:
        post_numbers: List (int). A list of post numbers.
    
    Returns: 
        A dictionary whose keys are the post numbers and values
        are vote counts (0 if the post is not found).
    """
    [raise_exception_if_number_has_incorrect_format(number) for number in post_numbers]
    return {number: grab.grab_votes(number) for number in post_numbers}

def get_comments(disqus_ids):
    """Get comment counts for some posts.

    Takes a dictionary of Disqus ID strings. If the Disqus 
    ID is in an incorrect format, an exception is raised. 
    If no post is found, None is returned for that particular post.

    Args:
        disqus_ids: Dictionary. Dictionary whose keys are post URLs
        and values are Disqus ID strings.
    
    Returns:
        A dictionary whose keys are the post URLs and values
        are comment counts (or None if the post is not found).
    """
    [raise_exception_if_url_is_not_ob_post_long_url(url) for url in disqus_ids.keys()]
    [raise_exception_if_disqus_id_has_incorrect_format(number) for number in disqus_ids.values()]
    comments = {}
    for url, disqus_id in disqus_ids.items():
        try:
            comments[url] = grab.grab_comments(disqus_id)
        except exceptions.InvalidResponseError:
            comments[url] = None
    return comments

def attach_edit_dates(post_list):
    """Attach "last modified" dates to a list of posts."""
    date_list = grab.grab_edit_dates()
    [p.set_edit_date(date_list[url]) for url, p in posts.items() if p is not None]
    return posts

def raise_exception_if_url_is_not_ob_post_long_url(url):
    if not isinstance(url, str):
        raise TypeError(f'expected URL to be string, got {url}')
    if not extract_post.is_ob_post_long_url(url):
        raise ValueError(f'expected URL to be ob post URL, got {url}')

def raise_exception_if_number_has_incorrect_format(number):
    if not isinstance(number, int):
        raise TypeError(f'expected number to be integer, got {number}')
    if not (9999 < number < 100000):
        raise ValueError(f'expected number to be 5-digit integer, got {number}')

def raise_exception_if_disqus_id_has_incorrect_format(disqus_id):
    if not isinstance(disqus_id, str):
        raise TypeError(f'expected Disqus ID to be string, got {disqus_id}')
    if not extract_post.is_valid_disqus_id(disqus_id):
        raise ValueError(f'Disqus ID {disqus_id} is not valid')