Public API Reference
====================

This page contains a full reference to obscraper's public API.

.. contents::
    :depth: 3
    :local:

Objects
*******

.. _post:

Post
####

.. autoclass:: obscraper.Post
    :members:

Functions
*********

.. _get-posts-by-names:

get_posts_by_names
##################

.. autofunction:: obscraper.get_posts_by_names


.. _get-vote-counts:

get_vote_counts
###############

.. autofunction:: obscraper.get_vote_counts


.. _get-comment-counts:

get_comment_counts
##################

.. autofunction:: obscraper.get_comment_counts


.. _get-edit-dates:

get_edit_dates
###############

.. autofunction:: obscraper.get_edit_dates


.. _get-all-posts:

get_all_posts
#############

.. autofunction:: obscraper.get_all_posts


.. _get-posts-by-edit-date:

get_posts_by_edit_date
######################

.. autofunction:: obscraper.get_posts_by_edit_date


.. _get-posts-by-urls: 

get_posts_by_urls
#################

.. autofunction:: obscraper.get_posts_by_urls


.. _get-post-by-name:

get_post_by_name
################

.. autofunction:: obscraper.get_post_by_name


.. _get-post-by-url:

get_post_by_url
###############

.. autofunction:: obscraper.get_post_by_url


.. _clear-cache:

clear_cache
###########

.. autofunction:: obscraper.clear_cache


.. _url-to-name:

url_to_name
###########

.. autofunction:: obscraper.url_to_name


.. _name-to-url:

name_to_url
###########

.. autofunction:: obscraper.name_to_url


Serializers
***********

.. _post-encoder:

PostEncoder
###########

.. autofunction:: obscraper.PostEncoder

.. _post-decoder:

PostDecoder
###########

.. autofunction:: obscraper.PostDecoder


Exceptions
**********

.. _invalid-response-error:

InvalidResponseError
####################

.. autoexception:: obscraper.InvalidResponseError


.. _attribute-not-found-error:

AttributeNotFoundError
######################

.. autoexception:: obscraper.AttributeNotFoundError


Constants
*********

.. _ob-post-url-pattern:

.. autodata:: obscraper.OB_POST_URL_PATTERN