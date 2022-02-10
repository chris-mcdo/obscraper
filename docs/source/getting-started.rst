Installation and Getting Started
================================

**Supported Python Versions**: 3.8+

**Supported Platforms**: Linux, Windows, MacOS

This page explains how to install obscraper and run some basic commands.

Install ``obscraper``
*********************

Install from `PyPI <https://pypi.org/project/obscraper/>`_:

.. code-block:: console

    $ python -m pip install obscraper
    $ python -m pip show obscraper

Alternatively, get the `source code <https://github.com/chris-mcdo/obscraper>`_:

.. code-block:: console

    $ git clone https://github.com/chris-mcdo/obscraper.git

Get a Single Post
*****************

Scrape data from a single
`post <https://www.overcomingbias.com/2006/11/introduction.html>`_:

.. code-block:: python

    >>> import obscraper
    >>> intro = obscraper.get_post_by_url('https://www.overcomingbias.com/2006/11/introduction.html')
    >>> f'{intro.title}, by {intro.author} ({intro.word_count} words)'
    'How To Join, by Robin Hanson (263 words)'

The post is represented as a :ref:`Post <post>` object:

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

:ref:`get_posts_by_urls <get-posts-by-urls>` and
:ref:`get_posts_by_names <get-posts-by-names>` let you get multiple posts by
their URLs / names.
The "name" of a post is its URL with the same-y parts chopped off:

.. code-block:: python

    >>> names = [
    ... '/2006/11/quiz_fox_or_hed',
    ... '/2011/04/the-seti-game',
    ... '/2013/10/stories-change-goals',
    ... ]
    >>> posts = obscraper.get_posts_by_names(names)

This returns a dictionary whose keys are the original URLs / names, and whose
values are the corresponding :ref:`Post <post>` objects:

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

Both :ref:`get_posts_by_urls <get-posts-by-urls>` and
:ref:`get_posts_by_edit_date <get-posts-by-edit-date>` return a dictionary of
labels (URLs / names) and posts.
This is the standard format for responses from the ``obscraper`` API.

Get All Posts
*************

To get a list of URLs and "last edited" dates for all posts (including
some no longer hosted on the overcomingbias site), you can use
:ref:`get_edit_dates <get-edit-dates>`:

.. code-block:: python

    >>> urls_and_dates = obscraper.get_edit_dates()
    >>> len(urls_and_dates)
    4353
    >>> {url: str(urls_and_dates[url]) for url in list(urls_and_dates)[:5]}
    {'/2022/01/best-case-contrarians': 
    '2022-01-16 21:55:04+00:00', 
    '/2022/01/much-talk-is-sales-patter': 
    '2022-01-14 20:46:35+00:00', 
    '/2022/01/old-man-rant': 
    '2022-01-13 15:21:33+00:00', 
    '/2022/01/my-11-bets-at-10-1-odds-on-10m-covid-deaths-by-2022': 
    '2022-01-12 19:15:10+00:00', 
    '/2022/01/to-innovate-unify-or-fragment': 
    '2022-01-11 01:03:44+00:00'}

You can download all posts indirectly by using :ref:`get_posts_by_edit_date
<get-posts-by-edit-date>`, or directly using :ref:`get_all_posts <get-all-posts>`:

.. code-block:: python

    >>> all_posts = obscraper.get_all_posts()
    >>> len(all_posts)
    3702
    >>> [p.title for p in all_posts.values() if 'Liability' in p.title]
    ['Innovation Liability Nightmare', 'Liability Insurance For All', 
    'Between Property and Liability', 'All Pay Liability', 
    'Require Legal Liability Insurance', 'For Doc Liability']

This may take a few (<10) minutes.

:ref:`get_all_posts <get-all-posts>` will send more than 4000 requests
to the overcomingbias site, and download ~100MB-1GB of data.
:ref:`get_edit_dates <get-edit-dates>` requires only 1 request to
the overcomingbias site, so should probably be preferred where possible.


Updating Vote and Comment Counts
********************************

Vote and comment counts are collected from separate APIs to the rest of
the post data.

They can be updated using :ref:`get_vote_counts <get-vote-counts>` and
:ref:`get_comment_counts <get-comment-counts>`:

.. code-block:: python

    >>> obscraper.get_vote_counts({'intro': intro.number})
    {'intro': 4}
    >>> obscraper.get_comment_counts({'intro': intro.disqus_id})
    {'intro': 20}

.. note:: 

    The vote count API appears to be broken for posts published after
    2021-03-17.


Representing Post Objects using JSON
************************************

To convert a list of :ref:`Post <post>` objects (or just one)
to the `JSON <https://www.json.org/>`_ format, use the
:ref:`PostEncoder <post-encoder>` class:

.. code-block:: python

    >>> import json
    >>> intro_json = json.dumps(intro, cls=obscraper.PostEncoder)
    >>> intro_json
    '{"name": "/2006/11/introduction", "number": 18402, ...}'

This is useful when storing posts for later:

..  code-block:: python

    >>> write_path = '2006-11-introduction.json'
    >>> with open(write_path, mode='w', encoding='utf8') as out_file:
    ...     json.dump(intro, out_file, cls=obscraper.PostEncoder, indent=4)

Also, the attributes of the post can be examined more easily in a file:

.. code-block:: javascript
    :caption: 2006-11-introduction.json

    {
        "name": "/2006/11/introduction",
        "number": 18402,
        "page_type": "post",
        ...
    }

To convert the JSON back into a :ref:`Post <post>` object, use
the :ref:`PostDecoder <post-decoder>` class:

.. code-block:: python

    >>> intro_json
    '{"name": "/2006/11/introduction", "number": 18402, ...}'
    >>> intro_decoded = json.loads(intro_json, cls=obscraper.PostDecoder)
    >>> type(intro_decoded)
    <class 'obscraper._post.Post'>
    >>> intro_decoded.title
    'How To Join'

Command Line Interface
**********************

``obscraper`` also comes with a command line interface:

.. code-block:: console

    $ obscraper --dates "November 25, 2016" "November 30, 2016"
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
                "name": "/2016/11/myplay",
                "number": 31449,
                "page_type": "post",
                ...
            }
        },
        ...
    ]

To see a full list of commands, use the -h / --help option.


Logging
*******

``obscraper`` uses python's inbuilt
`logging <https://docs.python.org/3/library/logging.html>`_ library to monitor
its activity.
This is mainly useful for debugging, but if you want you can see these logs
yourself by setting up a logger:

.. code-block:: python

    import logging
    handler = logging.FileHandler('logs.txt', encoding='utf-8')
    logger = logging.getLogger('obscraper')
    logger.setLevel(logging.DEBUG)
    logger.addHandler(handler)

    names = [
        '/2010/08/new-hard-steps-results', 
        '/2009/02/the-most-important-thing'
    ]
    posts = obscraper.get_posts_by_names(names)

    # Close logging file when finished!
    handler.close()
    logger.removeHandler(handler)

.. code-block:: text
    :caption: logs.txt

    AttributeNotFoundError raised when grabbing post /2009/02/the-most-important-thing
    Successfully grabbed post /2010/08/new-hard-steps-results

The ``urllib3`` library - which acts as the HTTP client - also uses logging.
You can get its logs by the same method as above.

Caching
*******

By default, ``obscraper`` caches recently accessed sites to increase
post retrieval speed and reduce the load on the overcomingbias site. 
This cache can be cleared using :ref:`clear_cache <clear-cache>`.
You may want to do this if the site has recently been updated, or a post
has been added.


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
:ref:`get_post_by_url <get-post-by-url>` will raise an
:ref:`InvalidResponseError <invalid-response-error>`. 

By contrast, :ref:`get_posts_by_urls <get-posts-by-urls>` will
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

The behaviour is similar for :ref:`get_post_by_name <get-post-by-name>` and
:ref:`get_posts_by_names <get-posts-by-names>`.
This is useful when you intend to download many posts, some of which may
not exist.


Continue Reading
****************

For more details on the ``obscraper`` public API, see the
:doc:`Public API Reference <api>`.
