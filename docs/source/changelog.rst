Changelog
=========

Versions follow the `Semantic Versioning 2.0.0 <https://semver.org/>`_
standard.

obscraper 0.3.0 (2022-02-03)
****************************

Breaking Changes
################

- :ref:`get_all_posts <get-all-posts>`,
  :ref:`get_posts_by_edit_date <get-posts-by-edit-date>` and
  :ref:`grab_edit_dates <grab-edit-dates>` now return post names rather than
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
