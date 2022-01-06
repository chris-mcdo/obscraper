"""Extract post URLs and last-edit dates from the site post list."""

from dateutil import parser as dt_parser # for easy date and time parsing

def extract_urls(xml):
    """Extract a list of post URLs from the sitemap (XML) file."""
    url_tags = xml.find_all("loc")
    url_strings = [tag.string for tag in url_tags]
    return url_strings

def extract_edit_dates(xml):
    """Extract a list of post edit dates from the sitemap (XML) file."""
    date_tags = xml.find_all("lastmod")
    dates = [ dt_parser.isoparse(tag.string) for tag in date_tags ]
    return dates
