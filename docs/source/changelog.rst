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


Improvements
############

- Let users specify the maximum number of threads used to download posts, via
  the ``max_workers`` optional argument.


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
