"""Get a list of posts by publish date or URL."""

from obscraper import future
from . import grab, extract_post, exceptions, utils

def get_all_posts():
    """Get all posts hosted on the overcomingbias site.
    
    Returns:
        A dictionary whose keys are the post URLs and whose 
        values are post.Post objects containing data scraped from
        the the URLs.
    """
    edit_dates = grab.grab_edit_dates()
    all_posts = get_posts_by_url(list(edit_dates.keys()))
    ob_posts = {url: p for url, p in all_posts.items() if p is not None}
    return attach_edit_dates(ob_posts)

def get_posts_by_url(urls):
    """Get list of posts identified by their URLs.
    
    The input should be a list of overcomingbias post "long"
    URLs. A long URL is one which contains the "name" of the post, e.g.
    https://www.overcomingbias.com/2011/05/jobs-kill-big-time.html.
    
    If one of the URLs is invalid, an exception is raised. 
    If a post or post attribute is not found, "None" is 
    returned for that particular post.

    Args:
        urls: List (String). A list of overcomingbias post "long" 
        URLs to scrape data for.

    Returns:
        A dictionary whose keys are the inputted URLs and whose 
        values are post.Post objects containing data scraped from
        the input URLs.
    """
    if not isinstance(urls, list):
        raise TypeError(f'expected urls to be list, got {type(urls)}')
    [raise_exception_if_url_is_not_ob_post_long_url(url) for url in urls]
    def get_post(url):
        """Get a post given its URL, returning None if not found."""
        try:
            return grab.grab_post_by_url(url)
        except (exceptions.AttributeNotFoundError, exceptions.InvalidResponseError):
            return None
    url_dict = {url: url for url in urls}
    posts = future.map_with_delay(func=get_post, arg_dict=url_dict, delay=0.02, max_workers=32)
    return attach_edit_dates(posts)

def get_posts_by_edit_date(start_date, end_date):
    """Get posts edited within a given date range.
    
    Args:
        start_date: aware datetime.datetime object. The start
        of the date range. 
        end_date: aware datetime.datetime object. The end of 
        the date range.
    
    Returns:
        A dictionary whose keys are the URLs of posts edited
        within the date range, and whose values are the 
        corresponding post data as post.Post objects.
    """
    raise_exception_if_date_has_incorrect_format(start_date, 'start_date')
    raise_exception_if_date_has_incorrect_format(end_date, 'end_date')
    if start_date > end_date:
        raise ValueError('end date is before start date')
    
    edit_dates = grab.grab_edit_dates()
    selected_urls = [url for url, edit_date in edit_dates.items() if start_date < edit_date < end_date]
    posts = get_posts_by_url(selected_urls)
    return attach_edit_dates(posts)    

def get_votes(post_numbers):
    """Get vote counts for some posts.
    
    If one of the numbers is in an incorrect format, an exception is
    raised. Unlike other functions, get_votes returns 0 (rather than
    None) when a post is not found. This is because it is not possible
    to determine whether a post exists or not from the vote count API;
    it will just return 0 in this case. 

    Args:
        disqus_ids: Dictionary. Dictionary whose keys are post URLs
        and values are post numbers.
    
    Returns: 
        A dictionary whose keys are the post URLs and values
        are vote counts (0 if the post is not found).
    """
    if not isinstance(post_numbers, dict):
        raise TypeError(f'expected post_numbers to be dict, got {type(post_numbers)}')
    [raise_exception_if_url_is_not_ob_post_long_url(url) for url in post_numbers.keys()]
    [raise_exception_if_number_has_incorrect_format(number) for number in post_numbers.values()]
    def get_vote(number):
        """Get a vote count given its post number, returning None if not found."""
        try:
            return grab.grab_votes(number)
        except (exceptions.AttributeNotFoundError, exceptions.InvalidAuthCodeError, exceptions.InvalidResponseError):
            return None
    votes = future.map_with_delay(get_vote, post_numbers, delay=0.02, max_workers=32)
    return votes

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
    if not isinstance(disqus_ids, dict):
        raise TypeError(f'expected disqus_ids to be dict, got {type(disqus_ids)}')
    [raise_exception_if_url_is_not_ob_post_long_url(url) for url in disqus_ids.keys()]
    [raise_exception_if_disqus_id_has_incorrect_format(number) for number in disqus_ids.values()]
    def get_comment(disqus_id):
        try:
            return grab.grab_comments(disqus_id)
        except exceptions.InvalidResponseError:
            return None
    comments = future.map_with_delay(get_comment, disqus_ids, delay=0.01, max_workers=50)
    return comments

def attach_edit_dates(posts):
    """Attach "last modified" dates to a list of posts.
    
    Args:
        posts: Dictionary. A dictionary whose keys are post
        URLs and whose values are corresponding post.Post objects.

    Returns:
        An updated dictionary of posts.
    """
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

def raise_exception_if_date_has_incorrect_format(d, variable_name):
    if not utils.is_aware_datetime(d):
        raise TypeError(f'expected {variable_name} to be aware datetime.datetime object, got {d}')