"""Get a list of posts by publish date or URL.

This interface is internal - implementation details may change.
"""

from obscraper import _future
from . import _exceptions, _extract_post, _grab, _utils


def get_all_posts():
    """Get all posts hosted on the overcomingbias site.

    This includes vote and comment counts for each post.

    Posts which are no longer hosted on the overcomingbias site are not
    included (i.e. posts by Eliezer Yudkowsky).

    Returns
    -------
    Dict[str, obscraper.Post]
        A dictionary whose keys are post URLs and whose values are the
        corresponding posts. "Last edit" dates are attached.
    """
    edit_dates = _grab.grab_edit_dates()
    all_posts = get_posts_by_urls(list(edit_dates.keys()))
    ob_posts = {url: p for url, p in all_posts.items() if p is not None}
    return ob_posts


def get_post_by_url(url):
    """Get a single post identified by its URL.

    The input should be an overcomingbias post URL, e.g.
    https://www.overcomingbias.com/2011/05/jobs-kill-big-time.html or
    https://www.overcomingbias.com/?p=27739.

    Parameters
    ---------
    url : str
        An overcomingbias post URL.

    Returns
    -------
    obscraper.Post
        The post corresponding to the input URL, with "last edit" date
        attached.

    Raises
    ------
    exceptions.InvalidResponseError
        If the URL returns a page that does not look like an
        overcomingbias post.
    exceptions.AttributeNotFoundError
        If a obscraper.Post attribute could not be extracted from the
        downloaded page.
    """
    raise_exception_if_url_is_not_valid_post_url(url)
    post = _grab.grab_post_by_url(url)
    return attach_edit_dates({post.url: post})[post.url]


def get_posts_by_urls(urls):
    """Get list of posts identified by their URLs.

    No exceptions are raised if a post or post attribute is not found -
    instead "None" is returned for that post.

    Parameters
    ---------
    urls : List[str]
        A list of overcomingbias post URLs to scrape data for.

    Returns
    -------
    Dict[str, obscraper.Post]
        A dictionary whose keys are the inputted URLs and whose values
        are the corresponding posts. "Last edit" dates are attached.
    """
    raise_exception_if_arg_is_not_type(urls, list, 'urls')
    for url in urls:
        raise_exception_if_url_is_not_valid_post_url(url)

    def get_post(url):
        """Get a post given its URL, returning None if not found."""
        try:
            return _grab.grab_post_by_url(url)
        except (_exceptions.AttributeNotFoundError,
                _exceptions.InvalidResponseError):
            return None
    url_dict = dict(zip(urls, urls))
    posts = _future.map_with_delay(
        func=get_post, arg_dict=url_dict, delay=0.02, max_workers=32)
    return attach_edit_dates(posts)


def get_posts_by_edit_date(start_date, end_date):
    """Get posts edited within a given date range.

    Parameters
    ----------
    start_date, end_date : datetime.datetime
        The start and end dates of the date range, as aware datetimes.

    Returns
    -------
    Dict[str, obscraper.Post]
        A dictionary whose keys are the URLs of posts edited within the
        date range, and whose values are the corresponding posts. "Last
        edit" dates are attached.

    Raises
    ------
    ValueError
        If start date is after end date.
    """
    raise_exception_if_date_has_incorrect_format(start_date, 'start_date')
    raise_exception_if_date_has_incorrect_format(end_date, 'end_date')
    if start_date > end_date:
        raise ValueError('end date is before start date')

    edit_dates = _grab.grab_edit_dates()
    selected_urls = [url for url, edit_date in edit_dates.items(
    ) if start_date < edit_date < end_date]
    posts = get_posts_by_urls(selected_urls)
    return attach_edit_dates(posts)


def get_votes(post_numbers):
    """Get vote counts for some posts.

    If one of the numbers is in an incorrect format, an exception is
    raised. Unlike other functions, ``get_votes`` returns 0 (rather than
    None) when a post is not found. This is because the vote count API
    returns a vote count of 0 for posts that do not exist - it is
    not possible to tell whether a post doesn't exist or if it just has
    zero votes.

    Parameters
    ---------
    post_numbers : Dict[str, int]
        Dictionary whose keys are arbitrary labels (e.g. the post URLs)
        and whose values are post numbers to get votes for.

    Returns
    -------
    Dict[str, int]
        A dictionary whose keys are the inputted labels URLs and whose
        values are the corresponding vote counts (int). The vote count
        is 0 if the post is not found.
    """
    raise_exception_if_arg_is_not_type(post_numbers, dict, 'post_numbers')
    for url, number in post_numbers.items():
        raise_exception_if_arg_is_not_type(url, str, 'post_numbers label')
        raise_exception_if_number_has_incorrect_format(number)

    def get_vote(number):
        """Get vote count, returning None if the post is not found."""
        try:
            return _grab.grab_votes(number)
        except (_exceptions.AttributeNotFoundError,
                _exceptions.InvalidAuthCodeError,
                _exceptions.InvalidResponseError):
            return None
    votes = _future.map_with_delay(
        get_vote, post_numbers, delay=0.02, max_workers=32)
    return votes


def get_comments(disqus_ids):
    """Get comment counts for some posts.

    Takes a dictionary of Disqus ID strings. If the Disqus
    ID is in an incorrect format, an exception is raised.
    If no post is found, None is returned for that particular post.

    Parameters
    ---------
    disqus_ids : Dict[str, str]
        Dictionary whose keys are arbitrary labels (e.g. the post URLs)
        and whose values are the the corresponding Disqus ID strings.

    Returns
    -------
    Dict[str, int]
        A dictionary whose keys are the inputted labels and whose values
        are the corresponding comment counts. The comment count is None
        if the post is not found.
    """
    raise_exception_if_arg_is_not_type(disqus_ids, dict, 'disqus_ids')
    for url, number in disqus_ids.items():
        raise_exception_if_arg_is_not_type(url, str, 'disqus_ids label')
        raise_exception_if_disqus_id_has_incorrect_format(number)

    def get_comment(disqus_id):
        try:
            return _grab.grab_comments(disqus_id)
        except _exceptions.InvalidResponseError:
            return None
    comments = _future.map_with_delay(
        get_comment, disqus_ids, delay=0.01, max_workers=50)
    return comments


def attach_edit_dates(posts):
    """Attach "last modified" dates to a list of posts.

    Parameters
    ---------
    posts : Dict[str, obscraper.Post]
        A dictionary whose keys are post URLs and whose values are the
        corresponding posts, or None.

    Returns
    -------
    Dict[str, obscraper.Post]
        An updated dictionary of posts, with edit dates attached.
    """
    date_list = _grab.grab_edit_dates()
    for post_or_none in posts.values():
        if post_or_none is not None:
            post_or_none.edit_date = date_list[post_or_none.url]
    return posts


def clear_cache():
    """Clear all cached data."""
    _grab.grab_post_by_url.cache_clear()
    _grab.grab_comments.cache_clear()
    _grab.grab_votes.cache_clear()
    _grab.grab_edit_dates.cache_clear()
    _grab.vote_auth_code.cache_clear()


def raise_exception_if_url_is_not_valid_post_url(url):
    """Raise an exception if a URL is not valid."""
    if not isinstance(url, str):
        raise TypeError(f'expected URL to be type str, got {type(url)}')
    if not _extract_post.is_valid_post_url(url):
        raise ValueError(
            f'expected URL to be overcomingbias post URL, got {url}')


def raise_exception_if_number_has_incorrect_format(number):
    """Raise an exception if a number has the wrong format."""
    if not isinstance(number, int):
        raise TypeError(
            f'expected number to be type int, got type {type(number)}')
    if not 9999 < number < 100000:
        raise ValueError(
            f'expected number to be 5-digit integer, got {number}')


def raise_exception_if_disqus_id_has_incorrect_format(disqus_id):
    """Raise an exception if a Diqus ID has the wrong format"""
    if not isinstance(disqus_id, str):
        raise TypeError(
            f'expected Disqus ID to be type str, got type {type(disqus_id)}')
    if not _extract_post.is_valid_disqus_id(disqus_id):
        raise ValueError(f'Disqus ID {disqus_id} is not valid')


def raise_exception_if_date_has_incorrect_format(date, variable_name):
    """Raise an exception if a datetime has the wrong format."""
    if not _utils.is_aware_datetime(date):
        raise TypeError(
            (f'expected {variable_name} to be type aware datetime.datetime, '
             f'got type {type(date)}')
        )


def raise_exception_if_arg_is_not_type(arg, expected_type, variable_name):
    """Raise an exception if an argument has the wrong type."""
    if not isinstance(arg, expected_type):
        raise TypeError(
            (f'expected {variable_name} to be type {expected_type}, '
             f'got {type(arg)}')
        )
