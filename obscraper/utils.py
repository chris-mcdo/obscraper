"""Miscellaneous utility functions"""

import datetime
import pytz
import re

def tidy_date(messy_date, timezone):
    """Convert verbose date string to an aware datetime.datetime object."""
    naive_date = datetime.datetime.strptime(messy_date, '%B %d, %Y %I:%M %p')
    return date_to_utc(naive_date, timezone)

def date_to_utc(localdt, timezone):
    """Convert naive datetime to UTC, remembering timezone quirks."""
    timezone = pytz.timezone(timezone)
    return timezone.localize(localdt).astimezone(pytz.utc)

def count_words(text, ignore=[]):
    """Count the number of words in a string, ignoring some."""
    text_without_hyphens = text.replace('-', '')
    text_without_punctuation = re.sub(r'[^a-zA-Z0-9]+', ' ', text_without_hyphens)
    words = len(
        [word for word in str.split(text_without_punctuation) if word not in ignore]
        )
    return words

def is_aware_datetime(d):
    """Test if an object is an "aware" datetime.datetime object."""
    if not isinstance(d, datetime.datetime):
        return False
    return d.tzinfo is not None and d.tzinfo.utcoffset(d) is not None
