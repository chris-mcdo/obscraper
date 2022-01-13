"""Extract post URLs and last-edit dates from the site post list.

This interface is internal - implementation details may change.
"""

import dateutil.parser


def extract_urls(xml):
    """Extract a list of post URLs from the sitemap (XML) file."""
    url_tags = xml.find_all("loc")
    url_strings = [tag.string for tag in url_tags]
    return url_strings


def extract_edit_dates(xml):
    """Extract a list of post edit dates from the sitemap (XML) file."""
    date_tags = xml.find_all("lastmod")
    dates = [dateutil.parser.isoparse(tag.string) for tag in date_tags]
    return dates
