Changelog
=========

Versions follow the `Semantic Versioning 2.0.0 <https://semver.org/>`_
standard.


obscraper 0.6.0 (2022-03-11)
****************************

Breaking changes
################

- Updated API: the ``internal_links`` and ``external_links`` attributes of
  :ref:`Post <post>` are now lists (possibly containing duplicates) rather than
  dictionaries.



obscraper 0.5.0 (2022-02-10)
****************************

Major update.

Improvements
############

- Asynchronous execution: internals now execute requests and postprocessing
  asynchronously using `trio <https://github.com/python-trio/trio>`_. This is at least
  10% faster than the previous multithreaded version.

- Improved tests: migrated all tests to pytest. Added more systematic testing of random
  posts.

- Sessions: internals now use (asynchronous) sessions, reducing the load on the
  overcomingbias server and increasing download speed.


Breaking changes
################

- Updated interface for consistency and clarity:

  - ``grab_edit_dates`` is now :ref:`get_edit_dates <get-edit-dates>`

  - ``get_votes`` and ``get_comments`` are now :ref:`get_vote_counts <get-vote-counts>`
    and :ref:`get_comment_counts <get-comment-counts>`

- Updated behaviour of :ref:`get_all_posts <get-all-posts>` to return None when the post
  could not be retrieved.

- Removed outdated ``max_workers`` argument from public API functions.


Trivial / internal changes
##########################

- Source code now follows the `black <https://github.com/psf/black>`_ format.


obscraper 0.4.0 (2022-02-06)
****************************

Features
########

- Added `logging <https://docs.python.org/3/library/logging.html>`_
  functionality, and documentation in the
  :doc:`Getting Started <getting-started>` guide.

Bug fixes
#########

- :ref:`AttributeNotFoundError <attribute-not-found-error>` exceptions are now
  caught when downloading multiple posts. This prevents crashes on "broken"
  posts, e.g. /2009/02/the-most-important-thing.

obscraper 0.3.0 (2022-02-03)
****************************

Breaking Changes
################

- :ref:`get_all_posts <get-all-posts>`,
  :ref:`get_posts_by_edit_date <get-posts-by-edit-date>` and
  *grab_edit_dates* now return post names rather than
  post URLs in their keys.

- "Short" URLs - the form overcomingbias.com/?p=12345 - are no longer accepted.
  This might change again in the future.

Features
########

- Add :ref:`get_post_by_name <get-post-by-name>` and
  :ref:`get_posts_by_names <get-posts-by-names>` to the public API.

- Add :ref:`OB_POST_URL_PATTERN <ob-post-url-pattern>` to the public API.

- Add :ref:`url_to_name <url-to-name>` and :ref:`name_to_url <name-to-url>`
  to the public API.

Improved Documentation
######################

- Add information on exceptions raised by public API functions.


Trivial / internal changes
##########################

- Most internal interfaces now use post names rather than URLs.


obscraper 0.2.0 (2022-01-19)
****************************

Breaking Changes
################

- :ref:`get_posts_by_urls <get-posts-by-urls>` will now fail when a post
  attribute can not be extracted from the post HTML, since this situation is
  technically a bug. Previously it returned None.

- The :ref:`Post <post>` name attribute now contains the year and month of
  publication, as in URLs. E.g. 'jobs-explain-lots' becomes
  '/2010/09/jobs-explain-lots'. This ensures the post URL can be reconstructed
  from the post name.

Improvements
############

- Let users specify the maximum number of threads used to download posts, via
  the ``max_workers`` optional argument.

- Remove repeated whitespace within the text, when getting post text as
  plaintext.

Trivial/Internal Changes
########################

- :ref:`Post <post>` now represents the post URL as a property rather than
  an attribute.

obscraper 0.1.3 (2022-01-18)
*****************************

First public release!

For the initial list of features, see :doc:`Getting Started <getting-started>`
and :doc:`Public API Reference <api>`.

.. Entry title format: obscraper 1.2.3 (release date)

.. Entry items:
.. Breaking Changes = backward-incompatible changes
.. Deprecations = functionality marked as deprecated
.. Features = Added new features
.. Improvements = Improvements to existing features
.. Bug Fixes
.. Improved Documentation
.. Trivial/Internal Changes
