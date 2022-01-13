"""Miscellaneous utility functions.

This interface is internal - implementation details may change.
"""

import re
import datetime
import pytz


def tidy_date(messy_date, timezone):
    """Convert verbose date string to aware datetime.datetime object."""
    naive_date = datetime.datetime.strptime(messy_date, '%B %d, %Y %I:%M %p')
    return date_to_utc(naive_date, timezone)


def date_to_utc(localdt, timezone):
    """Convert naive datetime to UTC, remembering timezone quirks."""
    timezone = pytz.timezone(timezone)
    return timezone.localize(localdt).astimezone(pytz.utc)


def count_words(text, ignore=None):
    """Count the number of words in a string, ignoring some."""
    if ignore is None:
        ignore = []
    text_without_punctuation = re.sub(r'[^a-zA-Z0-9\s]+', '', text)
    text_without_special_chars = re.sub(r'\s+', ' ', text_without_punctuation)
    words = len(
        [word for word in str.split(
            text_without_special_chars) if word not in ignore]
    )
    return words


def is_aware_datetime(date):
    """Test if an object is an "aware" datetime.datetime object."""
    if not isinstance(date, datetime.datetime):
        return False
    return date.tzinfo is not None and date.tzinfo.utcoffset(date) is not None
