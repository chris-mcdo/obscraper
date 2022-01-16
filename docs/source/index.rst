obscraper: scrape posts from the overcomingbias blog
====================================================

``obscraper`` provides a basic API for posts on the `overcomingbias <https://www.overcomingbias.com/>`_ blog.

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
    {'http://www.overcomingbias.com/2007/02/moderate_modera.html': 1, 
    'http://www.overcomingbias.com/2006/12/contributors_be.html': 1}
    >>> intro.comments
    20

And even easier to get all posts:

.. code-block:: python

Or a full list of post URLs and edit dates::

    >>> import obscraper
    >>> edit_dates = obscraper.grab_edit_dates()
    ...
    >>> len(edit_dates)
    4352
    >>> {url: str(edit_dates[url]) for url in list(edit_dates)[:5]}
    {'https://www.overcomingbias.com/2022/01/much-talk-is-sales-patter.html': 
    '2022-01-14 20:46:35+00:00', 
    'https://www.overcomingbias.com/2022/01/old-man-rant.html': 
    '2022-01-13 15:21:33+00:00', 
    'https://www.overcomingbias.com/2022/01/my-11-bets-at-10-1-odds-on-10m-covid-deaths-by-2022.html': 
    '2022-01-12 19:15:10+00:00', 
    'https://www.overcomingbias.com/2022/01/to-innovate-unify-or-fragment.html': 
    '2022-01-11 01:03:44+00:00', 
    'https://www.overcomingbias.com/2022/01/on-what-is-advice-useful.html': 
    '2022-01-10 18:46:26+00:00'}

For more, see :doc:`Getting Started <getting-started>`.

Features
********

- Get posts by their URLs or edit dates, or get all posts hosted on the
  overcomingbias site

- Provides detailed post metadata including post URLs, titles, authors, tags,
  publish dates, and last edit dates

- Provides summary of post content including full post text as HTML or
  plaintext, and a list of hyperlinks to other overcomingbias posts

- Multithreading and caching for fast downloads

- Use in scripts or the command line interface

- Comprehensively tested

.. TODO python versions support

Documentation
*************

.. TODO

See :doc:`getting-started` for an introduction to the package. 

.. Documentation is available at <LINK>, and includes
.. (bullet points for each doc type)

Bugs/Requests
*************

.. TODO Please use the GitHub <issue tracker> to submit bugs or request features.

Changelog
*********

.. TODO See the changelog for a list of fixes and enhancements of each version.

License
*******

Copyright (c) 2022 Christopher McDonald

Distributed under the terms of the `MIT <https://github.com/chris-mcdo/obscraper/blob/main/LICENSE>`_ license.

All overcomingbias posts are copyright the original authors.