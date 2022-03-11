obscraper: scrape posts from the overcomingbias blog
====================================================

``obscraper`` lets you scrape blog posts and associated metadata from the
`overcomingbias <https://www.overcomingbias.com/>`_ blog.

It's easy to get a single post:

.. code-block:: python

    >>> import obscraper
    >>> intro_url = 'https://www.overcomingbias.com/2006/11/introduction.html'
    >>> intro = obscraper.get_post_by_url(intro_url)
    >>> intro.title
    'How To Join'
    >>> intro.plaintext
    'How can we better believe what is true? ...'
    >>> intro.internal_links
    [
      'http://www.overcomingbias.com/2007/02/moderate_modera.html': 1,
      'http://www.overcomingbias.com/2006/12/contributors_be.html': 1
    ]
    >>> intro.comments
    20

Or a full list of post names and edit dates::

    >>> import obscraper
    >>> edit_dates = obscraper.get_edit_dates()
    ...
    >>> len(edit_dates)
    4352
    >>> {name: str(edit_dates[name]) for name in list(edit_dates)[:5]}
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

For more on how to use the package, see :doc:`Getting Started <getting-started>`.

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

See :doc:`Getting Started <getting-started>` for an introduction to the package. 

A full reference to the obscraper public API can be found at
:doc:`Public API Reference <api>`.

For the full details, check out the well-documented
`code <https://github.com/chris-mcdo/obscraper>`_.

Bugs/Requests
*************

Please use the `GitHub issue tracker <https://github.com/chris-mcdo/obscraper/issues>`_
to submit bugs or request features.

Changelog
*********

See the :doc:`Changelog <changelog>` for a list of fixes and enhancements of each
version.

License
*******

Copyright (c) 2022 Christopher McDonald

Distributed under the terms of the
`MIT <https://github.com/chris-mcdo/obscraper/blob/main/LICENSE>`_ license.

All overcomingbias posts are copyright the original authors.