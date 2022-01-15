Installation and Getting Started
================================

**Supported Python versions**: 3.9

**Supported platforms**: Windows

.. TODO test whether it works on linux, macOS

This page explains how to install obscraper and run some basic commands.

Install ``obscraper``
---------------------

Install from pypi:

.. code-block:: console

    $ python -m pip install obscraper


.. TODO how to check version?

Alternatively, get the source code:

.. code-block:: console

    $ git clone https://github.com/chris-mcdo/obscraper.git

Run from a script
-----------------

Scrape data from a post in 2 lines:

.. code-block:: python

    # sample_post.py
    import obscraper
    intro = obscraper.get_post_by_url('https://www.overcomingbias.com/2006/11/introduction.html')

    print(f'{intro.title} by {intro.author} ({intro.word_count} words)')

