"""Perform general web scraping tasks."""

import functools
import time
import requests
import bs4

MAX_TRIES = 10
RETRY_DELAY = 3.6

def retry_request(delay):
    """Retry http request until 429 response is no longer received."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(MAX_TRIES):
                response = func(*args, **kwargs)
                if response.status_code != 429:
                    break
                time.sleep(delay)
            return response
        return wrapper
    return decorator

@retry_request(RETRY_DELAY)
def http_get_request(url, headers={}):
    """Wrapper around requests.get."""
    headers.setdefault('user-agent', 'Mozilla/5.0',)
    response = requests.get(url, headers=headers)
    return response

@retry_request(RETRY_DELAY)
def http_head_request(url, headers={}):
    """Wrapper around requests.head."""
    headers.setdefault('user-agent', 'Mozilla/5.0')
    response = requests.head(url, headers=headers)
    return response

@retry_request(RETRY_DELAY)
def http_post_request(url, params, headers={}):
    """Wrapper around requests.post."""
    headers.setdefault('user-agent', 'Mozilla/5.0')
    response = requests.post(url, params=params, headers=headers)
    return response

def grab_xml_soup(url):
    """Grab an XML file and parse as a BeautifulSoup object."""
    return bs4.BeautifulSoup(grab_page_raw(url), 'lxml-xml')

def grab_page_raw(url):
    """Grab the raw HTML of a webpage."""
    return http_get_request(url).text

def grab_html_soup(url):
    """Grab an HTML file and parse as a BeautifulSoup object."""
    return bs4.BeautifulSoup(grab_page_raw(url), 'lxml')

def grab_status_code(url):
    """Get the status code returned by an arbitrary URL."""
    return http_head_request(url).status_code
