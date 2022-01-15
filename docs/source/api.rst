Public API Reference
====================

This page contains a full reference to obscraper's public API.

.. contents::
    :depth: 3
    :local:

Objects
*******

Post
####

.. autoclass:: obscraper.Post


Functions
*********

get_all_posts
#############

.. autofunction:: obscraper.get_all_posts


get_post_by_url
###############

.. autofunction:: obscraper.get_post_by_url

get_posts_by_urls
#################

.. autofunction:: obscraper.get_posts_by_urls

get_posts_by_edit_date
######################

.. autofunction:: obscraper.get_posts_by_edit_date

get_votes
#########

.. autofunction:: obscraper.get_votes

get_comments
############

.. autofunction:: obscraper.get_comments

clear_cache
###########

.. autofunction:: obscraper.clear_cache

grab_edit_dates
###############

.. autofunction:: obscraper.grab_edit_dates

Serializers
***********

PostEncoder
###########

.. autofunction:: obscraper.PostEncoder

PostDecoder
###########

.. autofunction:: obscraper.PostDecoder


Exceptions
**********

InvalidResponseError
####################

.. autoexception:: obscraper.InvalidResponseError

InvalidAuthCodeError
####################

.. autoexception:: obscraper.InvalidAuthCodeError

AttributeNotFoundError
######################

.. autoexception:: obscraper.AttributeNotFoundError
