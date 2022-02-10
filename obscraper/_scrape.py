"""Get a list of posts by publish date, name or URL.

This interface is internal - implementation details may change.
"""

import trio

from . import _assemble, _exceptions, _extract_post, _fetch, _utils


def get_posts_by_names(names):
    """Get list of posts identified by their names.

    No exceptions are raised if a post or post attribute is not found -
    instead "None" is returned for that post.

    Parameters
    ---------
    names : List[str]
        A list of overcomingbias post names to scrape data for.

    Returns
    -------
    Dict[str, obscraper.Post]
        A dictionary whose keys are the inputted names and whose values
        are the corresponding posts. "Last edit" dates are attached.

    Raises
    ------
    ValueError
        If any of the input names are not valid overcomingbias post
        names.
    """
    # Argument validation
    raise_exception_if_arg_is_not_type(names, list, "names")
    for name in names:
        raise_exception_if_name_is_not_valid_post_name(name)

    # Short-circuit if list is empty
    if names == []:
        return {}

    # Scraping
    names_dict = {name: name for name in names}
    posts = trio.run(_fetch.fetch_posts, names_dict)

    return posts


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
        A dictionary whose keys are the inputted labels and whose
        values are the corresponding vote counts (int). The vote count
        is 0 if the post is not found.

    Raises
    ------
    ValueError
        If any of the input post numbers are not valid.
    """
    # Argument validation
    raise_exception_if_arg_is_not_type(post_numbers, dict, "post_numbers")
    for url, number in post_numbers.items():
        raise_exception_if_arg_is_not_type(url, str, "post_numbers label")
        raise_exception_if_number_has_incorrect_format(number)

    # Short-circuit if dict is empty
    if post_numbers == {}:
        return {}

    # Run
    votes = trio.run(_fetch.fetch_vote_counts, post_numbers)

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

    Raises
    ------
    ValueError
        If any of the input Disqus IDs are not valid.
    """
    # Argument validation
    raise_exception_if_arg_is_not_type(disqus_ids, dict, "disqus_ids")
    for url, number in disqus_ids.items():
        raise_exception_if_arg_is_not_type(url, str, "disqus_ids label")
        raise_exception_if_disqus_id_has_incorrect_format(number)

    # Short-circuit if dict is empty
    if disqus_ids == {}:
        return {}

    # Run
    comments = trio.run(_fetch.fetch_comment_counts, disqus_ids)

    return comments


def get_edit_dates():
    """Get a list of post edit dates."""
    edit_dates = trio.run(_fetch.fetch_edit_dates)
    return edit_dates


def get_all_posts():
    """Get all posts hosted on the overcomingbias site.

    This includes vote and comment counts for each post, and their last edit dates.

    Posts which are no longer hosted on the overcomingbias site are returned as "None".

    Returns
    -------
    Dict[str, obscraper.Post]
        A dictionary whose keys are post names and whose values are the
        corresponding posts.
    """
    edit_dates = get_edit_dates()
    posts = get_posts_by_names(list(edit_dates.keys()))
    return posts


def get_post_by_name(name):
    """Get a single post by its name.

    Parameters
    ---------
    name : str
        An overcomingbias post name, e.g. '/2010/09/jobs-explain-lots'.

    Returns
    -------
    obscraper.Post
        A post with edit date attached.

    Raises
    ------
    ValueError
        If the input name is not a valid overcomingbias post name.
    obscraper.InvalidResponseError
        If the post could not be retrieved.
    """
    raise_exception_if_arg_is_not_type(name, str, "name")
    post = get_posts_by_names([name])[name]
    if post is None:
        raise _exceptions.InvalidResponseError("Could not retrieve" f" post {name}.")
    return post


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
        are the corresponding posts.

    Raises
    ------
    ValueError
        If any of the input URLs are not valid overcomingbias post URLs.
    """
    raise_exception_if_arg_is_not_type(urls, list, "urls")

    names = [_extract_post.url_to_name(url) for url in urls]
    posts_by_names = get_posts_by_names(names)
    posts_by_urls = {
        _extract_post.name_to_url(name): post for name, post in posts_by_names.items()
    }
    return posts_by_urls


def get_post_by_url(url):
    """Get a single post by its URL.

    Parameters
    ---------
    url : str
        An overcomingbias post URL.

    Returns
    -------
    obscraper.Post
        A post with edit date attached.

    Raises
    ------
    ValueError
        If the input URL is not a valid overcomingbias post URL.
    obscraper.InvalidResponseError
        If the post could not be retrieved.
    """
    raise_exception_if_arg_is_not_type(url, str, "url")
    post = get_posts_by_urls([url])[url]
    if post is None:
        raise _exceptions.InvalidResponseError("Could not retrieve post" f" {url}.")
    return post


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
    raise_exception_if_date_has_incorrect_format(start_date, "start_date")
    raise_exception_if_date_has_incorrect_format(end_date, "end_date")
    if start_date > end_date:
        raise ValueError("end date is before start date")

    edit_dates = get_edit_dates()
    selected_names = [
        name
        for name, edit_date in edit_dates.items()
        if start_date < edit_date < end_date
    ]
    posts = get_posts_by_names(selected_names)
    return posts


def clear_cache():
    """Clear all cached data."""
    _assemble.assemble_post.cache_clear()
    _assemble.assemble_vote_count.cache_clear()
    _assemble.assemble_comment_count.cache_clear()
    _assemble.assemble_edit_dates.cache_clear()
    _assemble.assemble_vote_auth.cache_clear()


def raise_exception_if_name_is_not_valid_post_name(name):
    """Raise an exception if a post name is not valid."""
    if not isinstance(name, str):
        raise TypeError(f"expected name to be type str, got {type(name)}")
    if not _extract_post.is_valid_post_name(name):
        raise ValueError(f"expected name to be overcomingbias post name, got {name}")


def raise_exception_if_number_has_incorrect_format(number):
    """Raise an exception if a number has the wrong format."""
    if not isinstance(number, int):
        raise TypeError(f"expected number to be type int, got type {type(number)}")
    if not 9999 < number < 100000:
        raise ValueError(f"expected number to be 5-digit integer, got {number}")


def raise_exception_if_disqus_id_has_incorrect_format(disqus_id):
    """Raise an exception if a Diqus ID has the wrong format"""
    if not isinstance(disqus_id, str):
        raise TypeError(
            f"expected Disqus ID to be type str, got type {type(disqus_id)}"
        )
    if not _extract_post.is_valid_disqus_id(disqus_id):
        raise ValueError(f"Disqus ID {disqus_id} is not valid")


def raise_exception_if_date_has_incorrect_format(date, variable_name):
    """Raise an exception if a datetime has the wrong format."""
    if not _utils.is_aware_datetime(date):
        raise TypeError(
            (
                f"expected {variable_name} to be type aware datetime.datetime, "
                f"got type {type(date)}"
            )
        )


def raise_exception_if_arg_is_not_type(arg, expected_type, variable_name):
    """Raise an exception if an argument has the wrong type."""
    if not isinstance(arg, expected_type):
        raise TypeError(
            (
                f"expected {variable_name} to be type {expected_type}, "
                f"got {type(arg)}"
            )
        )
