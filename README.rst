.. image:: https://raw.githubusercontent.com/chris-mcdo/obscraper/main/docs/source/img/logo.svg
   :target: https://obscraper.readthedocs.io/en/stable/
   :align: center
   :height: 200
   :alt: obscraper


obscraper: scrape posts from the overcomingbias blog
====================================================

.. image:: https://img.shields.io/pypi/v/obscraper.svg
    :target: https://pypi.org/project/obscraper/
    :alt: Project Version on PyPI

.. image:: https://img.shields.io/pypi/pyversions/obscraper.svg
    :target: https://pypi.org/project/obscraper/
    :alt: Supported Python Versions

.. image:: https://github.com/chris-mcdo/obscraper/workflows/tests/badge.svg
  :target: https://github.com/chris-mcdo/obscraper/actions?query=workflow%3Atests
  :alt: Unit Tests

.. image:: https://readthedocs.org/projects/obscraper/badge/?version=latest
  :target: https://obscraper.readthedocs.io/en/latest/?badge=latest
  :alt: Documentation Status

.. image:: https://codecov.io/gh/chris-mcdo/obscraper/branch/main/graph/badge.svg
  :target: https://codecov.io/gh/chris-mcdo/obscraper
  :alt: Unit Test Coverage
  
.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
  :target: https://github.com/psf/black
  :alt: Code Style: Black

.. image:: https://img.shields.io/badge/license-MIT-purple
  :target: https://github.com/chris-mcdo/obscraper/blob/main/LICENSE
  :alt: MIT License


``obscraper`` lets you scrape blog posts and associated metadata from the
`overcomingbias <https://www.overcomingbias.com/>`_ blog.

It's easy to get a single post::

    >>> import obscraper
    >>> intro_url = 'https://www.overcomingbias.com/2006/11/introduction.html'
    >>> post = obscraper.get_post_by_url(intro_url)
    >>> post.title
    'How To Join'
    >>> post.plaintext
    'How can we better believe what is true? ...'
    >>> post.internal_links
    {'http://www.overcomingbias.com/2007/02/moderate_modera.html': 1, 
    'http://www.overcomingbias.com/2006/12/contributors_be.html': 1}
    >>> post.comments
    20

Or a full list of post URLs and edit dates::

    >>> import obscraper
    >>> edit_dates = obscraper.get_edit_dates()
    ...
    >>> len(edit_dates)
    4352
    >>> {url: str(edit_dates[url]) for url in list(edit_dates)[:5]}
    {'/2022/01/much-talk-is-sales-patter':
    '2022-01-14 20:46:35+00:00',
    '/2022/01/old-man-rant':
    '2022-01-13 15:21:33+00:00',
    '/2022/01/my-11-bets-at-10-1-odds-on-10m-covid-deaths-by-2022':
    '2022-01-12 19:15:10+00:00',
    '/2022/01/to-innovate-unify-or-fragment':
    '2022-01-11 01:03:44+00:00',
    '/2022/01/on-what-is-advice-useful':
    '2022-01-10 18:46:26+00:00'}

Features
********

- Get posts by their URLs or edit dates, or get all posts hosted on the
  overcomingbias site

- Provides detailed post metadata including post URLs, titles, authors, tags,
  publish dates, and last edit dates

- Provides summary of post content including full post text as HTML or
  plaintext, and a list of hyperlinks to other overcomingbias posts

- Asynchronous execution and caching for fast downloads

- Use via ``import obscraper`` or the simple command line interface

- Comprehensively tested

- Supports python 3.8+

Documentation
*************

Read the full documentation `here <https://obscraper.readthedocs.io/en/stable/>`_,
including the `Installation and Getting Started Guide
<https://obscraper.readthedocs.io/en/stable/getting-started.html>`_ and the
`Public API Reference <https://obscraper.readthedocs.io/en/stable/api.html>`_.


Bugs/Requests
*************

Please use the `GitHub issue tracker <https://github.com/chris-mcdo/obscraper/issues>`_
to submit bugs or request features.

Changelog
*********

See the `Changelog <https://obscraper.readthedocs.io/en/stable/changelog.html>`_
for a list of fixes and enhancements at each version.

License
*******

Copyright (c) 2022 Christopher McDonald

Distributed under the terms of the
`MIT <https://github.com/chris-mcdo/obscraper/blob/main/LICENSE>`_ license.

All overcomingbias posts are copyright the original authors.
