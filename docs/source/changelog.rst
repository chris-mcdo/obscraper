Changelog
=========

Versions follow the `Semantic Versioning 2.0.0 <https://semver.org/>`_ standard.

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
