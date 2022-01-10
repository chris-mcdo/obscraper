"""Get a list of posts by publish date or URL."""

from obscraper import future
from . import grab, extract_post, exceptions, utils


def get_all_posts():
    """Get all posts hosted on the overcomingbias site.

    Returns
    -------
    posts : dict
        A dictionary whose keys are post URLs (str) and whose values are
        the corresponding posts (post.Post).
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

    If a post or post attribute is not found, "None" is returned for
    that post.

    Parameter
    ---------
    urls : list of str
        A list of overcomingbias post "long" URLs to scrape data for.

    Returns
    -------
    posts : dict
        A dictionary whose keys are the inputted URLs (str) and whose
        values are the corresponding posts (post.Post).
    """
    raise_exception_if_arg_is_not_type(urls, list, 'urls')
    for url in urls:
        raise_exception_if_url_is_not_ob_post_long_url(url)

    def get_post(url):
        """Get a post given its URL, returning None if not found."""
        try:
            return grab.grab_post_by_url(url)
        except (exceptions.AttributeNotFoundError,
                exceptions.InvalidResponseError):
            return None
    url_dict = {url: url for url in urls}
    posts = future.map_with_delay(
        func=get_post, arg_dict=url_dict, delay=0.02, max_workers=32)
    return attach_edit_dates(posts)


def get_posts_by_edit_date(start_date, end_date):
    """Get posts edited within a given date range.

    Parameters
    ----------
    start_date, end_date : aware datetime.datetime
        The start and end dates of the date range.

    Returns
    -------
    posts : dict
        A dictionary whose keys are the URLs of posts edited within the
        date range (str), and whose values are the corresponding posts
        (post.Post).

    Raises
    ------
    ValueError
        If start date is after end date.
    """
    raise_exception_if_date_has_incorrect_format(start_date, 'start_date')
    raise_exception_if_date_has_incorrect_format(end_date, 'end_date')
    if start_date > end_date:
        raise ValueError('end date is before start date')

    edit_dates = grab.grab_edit_dates()
    selected_urls = [url for url, edit_date in edit_dates.items(
    ) if start_date < edit_date < end_date]
    posts = get_posts_by_url(selected_urls)
    return attach_edit_dates(posts)


def get_votes(post_numbers):
    """Get vote counts for some posts.

    If one of the numbers is in an incorrect format, an exception is
    raised. Unlike other functions, get_votes returns 0 (rather than
    None) when a post is not found. This is because it is not possible
    to determine whether a post exists or not from the vote count API;
    it will just return 0 in this case.

    Parameter
    ---------
    post_numbers : dict
        Dictionary whose keys are post URLs (str) and whose values are
        post numbers to get votes for (int).

    Returns
    -------
    votes : dict
        A dictionary whose keys are the post URLs (str) and whose values
        are corresponding vote counts (int). The vote count is 0 if the
        post is not found.
    """
    raise_exception_if_arg_is_not_type(post_numbers, dict, 'post_numbers')
    for url, number in post_numbers.items():
        raise_exception_if_url_is_not_ob_post_long_url(url)
        raise_exception_if_number_has_incorrect_format(number)

    def get_vote(number):
        """Get vote count, returning None if the post is not found."""
        try:
            return grab.grab_votes(number)
        except (exceptions.AttributeNotFoundError,
                exceptions.InvalidAuthCodeError,
                exceptions.InvalidResponseError):
            return None
    votes = future.map_with_delay(
        get_vote, post_numbers, delay=0.02, max_workers=32)
    return votes


def get_comments(disqus_ids):
    """Get comment counts for some posts.

    Takes a dictionary of Disqus ID strings. If the Disqus
    ID is in an incorrect format, an exception is raised.
    If no post is found, None is returned for that particular post.

    Parameter
    ---------
    disqus_ids : dict
        Dictionary whose keys are post URLs (str) and whose values are
        Disqus ID strings (str).

    Returns
    -------
    comments : dict
        A dictionary whose keys are the post URLs (str) and whose values
        are corresponding comment counts (int). The comment count is
        None if the post is not found.
    """
    raise_exception_if_arg_is_not_type(disqus_ids, dict, 'disqus_ids')
    for url, number in disqus_ids.items():
        raise_exception_if_url_is_not_ob_post_long_url(url)
        raise_exception_if_disqus_id_has_incorrect_format(number)

    def get_comment(disqus_id):
        try:
            return grab.grab_comments(disqus_id)
        except exceptions.InvalidResponseError:
            return None
    comments = future.map_with_delay(
        get_comment, disqus_ids, delay=0.01, max_workers=50)
    return comments


def attach_edit_dates(posts):
    """Attach "last modified" dates to a list of posts.

    Parameter
    ---------
    posts : dict
        A dictionary whose keys are post URLs (str) and whose values are
        the corresponding posts (post.Post).

    Returns
    -------
    posts : dict
        An updated dictionary of posts, with edit dates attached.
    """
    date_list = grab.grab_edit_dates()
    for url, post_or_none in posts.items():
        if post_or_none is not None:
            post_or_none.edit_date = date_list[url]
    return posts


def raise_exception_if_url_is_not_ob_post_long_url(url):
    """Raise an exception if a URL is not a post "long" URL."""
    if not isinstance(url, str):
        raise TypeError(f'expected URL to be type str, got {type(url)}')
    if not extract_post.is_valid_post_long_url(url):
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
    if not extract_post.is_valid_disqus_id(disqus_id):
        raise ValueError(f'Disqus ID {disqus_id} is not valid')


def raise_exception_if_date_has_incorrect_format(date, variable_name):
    """Raise an exception if a datetime has the wrong format."""
    if not utils.is_aware_datetime(date):
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
