Installation and Getting Started
================================

**Supported Python Versions**: 3.8+

**Supported Platforms**: Linux, Windows, MacOS

This page explains how to install obscraper and run some basic commands.

Install ``obscraper``
*********************

Install from PyPI:

.. code-block:: console

    $ python -m pip install obscraper
    $ python -m pip show obscraper

Alternatively, get the source code:

.. code-block:: console

    $ git clone https://github.com/chris-mcdo/obscraper.git

Get a Single Post
*****************

Scrape data from a single post:

.. code-block:: python

    >>> import obscraper
    >>> intro = obscraper.get_post_by_url('https://www.overcomingbias.com/2006/11/introduction.html')
    >>> f'{intro.title}, by {intro.author} ({intro.word_count} words)'
    'How To Join, by Robin Hanson (263 words)'

The post is represented as an :ref:`obscraper.Post <post>` object:

.. code-block:: python

    >>> type(intro)
    <class 'obscraper._post.Post'>
    >>> f'{intro.publish_date}'
    '2006-11-20 11:00:00+00:00'
    >>> intro.tags
    ['meta']
    >>> intro.text_html
    '<div class="entry-content">\n<p>How can we better believe what is true? ...'
    >>> intro.plaintext
    'How can we better believe what is true? ...'

A full list of post attributes can be found in the :doc:`API Reference <api>`.

Get Multiple Posts
******************

To get multiple posts by their URLs, use :ref:`obscraper.get_posts_by_urls <get-posts-by-urls>`:

.. code-block:: python

    >>> urls = [
    ... 'https://www.overcomingbias.com/2006/11/quiz_fox_or_hed.html',
    ... 'https://www.overcomingbias.com/2011/04/the-seti-game.html',   
    ... 'https://www.overcomingbias.com/2013/10/stories-change-goals.html',
    ... ]
    >>> posts = obscraper.get_posts_by_urls(urls)

This returns a dictionary whose keys are the original URLs, and whose values
are the corresponding :ref:`obscraper.Post <post>` objects:

.. code-block:: python

    >>> type(posts)
    <class 'dict'>
    >>> [p.title for p in posts.values()]
    ['Quiz: Fox or Hedgehog?', 'The SETI Game', 'Stories Change Goals']
    >>> [p.word_count for p in posts.values()]
    [980, 792, 316]

Alternatively, you can get posts by their "last edited" dates:

.. code-block:: python

    >>> import datetime
    >>> today = datetime.datetime.now(tz=datetime.timezone.utc)
    >>> one_year_ago = today - 365 * datetime.timedelta(days=1)
    >>> posts = obscraper.get_posts_by_edit_date(start_date=one_year_ago, end_date=today)
    >>> len(posts)
    142
    >>> [p.title for p in posts.values() if p is not None][:5]
    ['Best Case Contrarians', 'Much Talk Is Sales Patter', 'My Old Man Rant',
    'My 11 Bets at 10-1 Odds On 10M Covid deaths by 2022', 
    'To Innovate, Unify or Fragment?']

Like :ref:`obscraper.get_posts_by_urls <get-posts-by-urls>`,
:ref:`obscraper.get_posts_by_edit_date <get-posts-by-edit-date>` also returns
a dictionary of labels (URLs) and posts.
This is the standard format for responses from the ``obscraper`` API.

Get All Posts
*************

To get a list of URLs and "last edited" dates for all posts (including
some no longer hosted on the overcomingbias site), you can use
:ref:`obscraper.grab_edit_dates <grab-edit-dates>`:

.. code-block:: python

    >>> urls_and_dates = obscraper.grab_edit_dates()
    >>> len(urls_and_dates)
    4353
    >>> {url: str(urls_and_dates[url]) for url in list(urls_and_dates)[:5]}
    {'https://www.overcomingbias.com/2022/01/best-case-contrarians.html': 
    '2022-01-16 21:55:04+00:00', 
    'https://www.overcomingbias.com/2022/01/much-talk-is-sales-patter.html': 
    '2022-01-14 20:46:35+00:00', 
    'https://www.overcomingbias.com/2022/01/old-man-rant.html': 
    '2022-01-13 15:21:33+00:00', 
    'https://www.overcomingbias.com/2022/01/my-11-bets-at-10-1-odds-on-10m-covid-deaths-by-2022.html': 
    '2022-01-12 19:15:10+00:00', 
    'https://www.overcomingbias.com/2022/01/to-innovate-unify-or-fragment.html': 
    '2022-01-11 01:03:44+00:00'}

You can download all posts indirectly by using :ref:`obscraper.get_posts_by_edit_date
<get-posts-by-edit-date>`, or directly using :ref:`obscraper.get_all_posts <get-all-posts>`:

.. code-block:: python

    >>> all_posts = obscraper.get_all_posts()
    >>> len(all_posts)
    3702
    >>> [p.title for p in all_posts.values() if 'Liability' in p.title]
    ['Innovation Liability Nightmare', 'Liability Insurance For All', 
    'Between Property and Liability', 'All Pay Liability', 
    'Require Legal Liability Insurance', 'For Doc Liability']

This may take a few (<10) minutes.

:ref:`obscraper.get_all_posts <get-all-posts>` will send more than 4000 requests
to the overcomingbias site, and download ~100MB-1GB of data.
:ref:`obscraper.grab_edit_dates <grab-edit-dates>` requires only 1 request to
the overcomingbias site, so should probably be preferred where possible.

Representing Post Objects using JSON
************************************

To convert a list of :ref:`obscraper.Post <post>` objects (or just one)
to the `JSON <https://www.json.org/>`_ format, use the
:ref:`obscraper.PostEncoder <post-encoder>` class:

.. code-block:: python

    >>> import json
    >>> intro_json = json.dumps(intro, cls=obscraper.PostEncoder)
    >>> intro_json
    '{"url": "https://www.overcomingbias.com/2006/11/introduction.html", ...'

This is useful for storing posts for later:

..  code-block:: python

    >>> write_path = '2006-11-introduction.json'
    >>> with open(write_path, mode='w', encoding='utf8') as out_file:
    ...     json.dump(intro, out_file, cls=obscraper.PostEncoder, indent=4)

Also, the attributes of the post can be examined more easily in a file:

.. code-block:: javascript
    :caption: 2006-11-introduction.json

    {
        "url": "https://www.overcomingbias.com/2006/11/introduction.html",
        "name": "introduction",
        "number": 18402,
        "page_type": "post",
        ...
    }

To convert the JSON back into an :ref:`obscraper.Post <post>` object, use
the :ref:`obscraper.PostDecoder <post-decoder>` class:

.. code-block:: python

    >>> intro_json
    '{"url": "https://www.overcomingbias.com/2006/11/introduction.html", ...'
    >>> intro_decoded = json.loads(intro_json, cls=obscraper.PostDecoder)
    >>> type(intro_decoded)
    <class 'obscraper._post.Post'>
    >>> intro_decoded.title
    'How To Join'

Command Line Interface
**********************

``obscraper`` also comes with a command line interface:

.. code-block:: console

    $ python -m obscraper --dates "November 25, 2016" "November 30, 2016"
    Getting posts edited between 2016-11-25 00:00:00+00:00 and 2016-11-30 00:00:00+00:00...
    Writing posts to posts.json...
    Posts successfully written to file.

You can use the CLI to get posts by their URLs or their edit dates, or
to download all posts.
By default the results are stored in a posts.json file in the current
directory:

.. code-block:: javascript
    :caption: posts.json

    [
        {
            "url": "https://www.overcomingbias.com/2016/11/myplay.html",
            "post": {
                "url": "https://www.overcomingbias.com/2016/11/myplay.html",
                "name": "myplay",
                "number": 31449,
                "page_type": "post",
                ...
            }
        },
        ...
    ]

To see a full list of commands, use the -h / --help option.

Caching
*******

By default, ``obscraper`` caches recently accessed sites to increase
speed and reduce the load on the overcomingbias site. 
This cache can be cleared using :ref:`obscraper.clear_cache <clear-cache>`.
You may want to do this if the site has recently been updated, or a post
has been added.

Updating Vote and Comment Counts
********************************

Vote and comment counts are collected from separate APIs to the rest of
the post data.

They can be updated using the :ref:`obscraper.get_votes <get-votes>` and
:ref:`obscraper.get_comments <get-comments>` functions:

.. code-block:: python

    >>> obscraper.get_votes({'intro': intro.number})
    {'intro': 4}
    >>> obscraper.get_comments({'intro': intro.disqus_id})
    {'intro': 20}

.. note:: 

    The vote count API appears to be broken for posts published after
    2021-03-17.

Errors and Exceptions
*********************

``obscraper`` tries to catch most errors before attempting to download
anything. For example: 

.. code-block:: python

    >>> obscraper.get_post_by_url(12345)
    Traceback ...
    TypeError: expected URL to be type str, got <class 'int'>
    >>> obscraper.get_post_by_url('https://www.overcomingbias.com/blah')
    Traceback ... 
    ValueError: expected URL to be overcomingbias post URL, got 
    https://www.overcomingbias.com/blah

When a URL is not found on the overcomingbias site,
:ref:`obscraper.get_post_by_url <get-post-by-url>` will raise an
:ref:`obscraper.InvalidResponseError <invalid-response-error>`. 

By contrast, :ref:`obscraper.get_posts_by_urls <get-posts-by-urls>` will
just return None for that particular post:

.. code-block:: python

    >>> urls = [
    ... 'https://www.overcomingbias.com/2006/11/quiz_fox_or_hed.html',
    ... 'https://www.overcomingbias.com/2011/04/the-seti-game.html',   
    ... 'https://www.overcomingbias.com/2013/10/not-a-real-post.html',
    ... ]
    >>> posts = obscraper.get_posts_by_urls(urls)
    >>> posts[urls[0]].title
    'Quiz: Fox or Hedgehog?'
    >>> posts[urls[2]]
    None

This is useful when you intend to download many posts, some of which may
not exist.

Continue Reading
****************

For more details on the ``obscraper`` public API, see the :doc:`Public API Reference <api>`.
