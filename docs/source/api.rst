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

.. _get-all-posts:

get_all_posts
#############

.. autofunction:: obscraper.get_all_posts

.. _get-post-by-url:

get_post_by_url
###############

.. autofunction:: obscraper.get_post_by_url

.. _get-posts-by-urls: 

get_posts_by_urls
#################

.. autofunction:: obscraper.get_posts_by_urls

.. _get-posts-by-edit-date:

get_posts_by_edit_date
######################

.. autofunction:: obscraper.get_posts_by_edit_date

.. _get-votes:

get_votes
#########

.. autofunction:: obscraper.get_votes

.. _get-comments:

get_comments
############

.. autofunction:: obscraper.get_comments

.. _clear-cache:

clear_cache
###########

.. autofunction:: obscraper.clear_cache

.. _grab-edit-dates:

grab_edit_dates
###############

.. autofunction:: obscraper.grab_edit_dates

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

.. _invalid-auth-code-error:

InvalidAuthCodeError
####################

.. autoexception:: obscraper.InvalidAuthCodeError

.. _attribute-not-found-error:

AttributeNotFoundError
######################

.. autoexception:: obscraper.AttributeNotFoundError
