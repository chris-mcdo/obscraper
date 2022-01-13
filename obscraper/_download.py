"""Perform general web scraping tasks.

This interface is internal - implementation details may change.
"""
import functools
import random
import time
import requests
import bs4

START_DELAY = 0.04
INCREASE_FACTOR = 4
MAX_DELAY = 3


def retry_request(func):
    """Retry HTTP request until 429 response is no longer received."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        delay = START_DELAY
        while delay < MAX_DELAY:
            response = func(*args, **kwargs)
            if response.status_code != 429:
                break
            time.sleep(delay * (1 + random.random()) / 2)
            delay = delay * INCREASE_FACTOR
        return response
    return wrapper


@retry_request
def http_get_request(url, headers=None):
    """Wrapper around requests.get."""
    if headers is None:
        headers = {}
    headers.setdefault('user-agent', 'Mozilla/5.0',)
    response = requests.get(url, headers=headers)
    return response


@retry_request
def http_post_request(url, params, headers=None):
    """Wrapper around requests.post."""
    if headers is None:
        headers = {}
    headers.setdefault('user-agent', 'Mozilla/5.0')
    response = requests.post(url, params=params, headers=headers)
    return response


def grab_xml_soup(url):
    """Download an XML file and parse as a bs4.BeautifulSoup object."""
    return bs4.BeautifulSoup(grab_page_raw(url), 'lxml-xml')


def grab_page_raw(url):
    """Download the raw HTML of a webpage."""
    return http_get_request(url).text


def grab_html_soup(url):
    """Download an HTML file and parse as a bs4.BeautifulSoup object."""
    return bs4.BeautifulSoup(grab_page_raw(url), 'lxml')
