"""Get a list of posts by publish date or URL."""

import math
import datetime
from . import grab, exceptions, extract_page, utils

# Maximum number of pages to look through on a single run. 
MAX_PAGES = 1000
MIN_DATE = datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc)

def get_posts_by_url(urls):
    """Get list of posts identified by their URLs.
    
    Args:
        urls: List (String). A list of post URLs to scrape data for.

    Returns:
        urls: List (String). A list of post URLs to scrape data for.
    """
    (raise_exception_if_url_is_not_ob_post_url(url) for url in urls)
    posts = [grab.grab_post_by_url(url) for url in urls]
    return attach_edit_dates(posts)

# TODO decide whether to remove date-related functionality, and just use
# page numbers
def get_posts_by_date(start_date=None, end_date=None):
    """Get list of posts published within a date range.
    
    Args:
        start_date: aware datetime.datetime object. Defines the start of 
        the date range to look for posts in.
        end_date: aware datetime.datetime object. Defines the end of the 
        date range to look for posts in.

    Returns:
        A list of Post objects scraped from the web. 
    """
    raise_exception_if_date_has_incorrect_format(start_date)
    raise_exception_if_date_has_incorrect_format(end_date)

    if start_date is not None and end_date is not None:
        if start_date > end_date:
            raise ValueError('start date is later than end date')

    datetime_now = datetime.datetime.now(datetime.timezone.utc)
    if start_date is None:
        start_date = MIN_DATE
    if end_date is None:
        end_date = datetime_now
    
    # What page to start on?
    if end_date >= datetime_now:
        start_page = 1
    else:
        start_page = get_start_page(end_date)

    # No pages have posts before end_date: return empty list
    if start_page is None:
        return []

    posts = []
    for page in range(start_page, start_page + MAX_PAGES):
        try:
            page_posts = grab.grab_all_posts_on_page(page)
            page_dates = [post.publish_date for post in page_posts]
            posts.extend([post for post, date in zip(page_posts, page_dates) if start_date < date < end_date])
            if min(page_dates) < start_date:
                break
        except exceptions.InvalidResponseError:
            break
    return attach_edit_dates(posts)

def get_start_page(end_date, page = 1, step_size = 1):
    """Efficiently find the first page with posts before a given date.
    
    Args:
        end_date: aware datetime.datetime object. The first page containing
        a post before this date is returned.
        page: int. The "current" page being checked.
        step_size: int. How many pages were "jumped" from the previous page. 
    
    Return: 
        A tuple containing the page number and the page HTML of the first 
        page containing a post before the end_date. Page HTML is None if
        no posts before end date are found. 
    """
    try:
        dates = grab.grab_publish_dates(page)
        before_end_date = min(dates) < end_date
        if before_end_date:
            if step_size == 1:
                # Finished
                return page
            # Return to previous page and reduce step size
            next_step_size = 1
            next_page = page - step_size + next_step_size
        else:
            # Increase step size, move to next page
            next_step_size = math.floor(math.exp(math.log(step_size) + 1)) # increase step size
            next_page = page + next_step_size
    except exceptions.InvalidResponseError:
        # Page number is greater than number of pages
        if step_size == 1:
            # No pages are before end date: return None
            return None
        # Return to previous page and take a smaller step forward
        next_step_size = 1
        next_page = page - step_size + next_step_size
    return get_start_page(end_date, next_page, next_step_size)

def get_votes(post_numbers):
    """Get vote counts for some posts.
    
    Args:
        post_numbers: List (int). A list of post numbers.
    
    Returns: 
        A dictionary whose keys are the post numbers and values
        are vote counts.
    """
    (raise_exception_if_number_has_incorrect_format(number) for number in post_numbers)
    return {number: grab.grab_votes(number) for number in post_numbers}

def get_comments(post_numbers):
    """Get comment counts for some posts.
    
    Args:
        post_numbers: List (int). A list of post numbers.
    
    Returns:
        A dictionary whose keys are the post numbers and values
        are comment counts.
    """
    (raise_exception_if_number_has_incorrect_format(number) for number in post_numbers)
    return {number: grab.grab_comments(number) for number in post_numbers}

def attach_edit_dates(post_list):
    """Attach "last modified" dates to a list of posts."""
    date_list = grab.grab_edit_dates()
    for post in post_list:
            post.set_edit_date(date_list[post.url])
    return post_list

def raise_exception_if_number_has_incorrect_format(number):
    if not isinstance(number, int):
        raise TypeError(f'expected number to be integer, got {number}')
    if not (9999 < number < 100000):
        raise ValueError(f'expected number to be 5 digits, got {number}')

def raise_exception_if_url_is_not_ob_post_url(url):
    if not isinstance(url, str):
        raise TypeError(f'expected URL to be string, got {url}')
    if not extract_page.is_ob_post_url(url):
        raise ValueError(f'expected URL to be OB post URL, got {url}')

def raise_exception_if_date_has_incorrect_format(d):
    if d is not None and not utils.is_aware_datetime(d):
        raise TypeError(f'date {d} is not an aware datetime object or None')
