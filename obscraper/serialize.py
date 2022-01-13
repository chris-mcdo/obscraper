"""Encode and decode post.Post objects."""

import json
import dataclasses
import datetime
import dateutil.parser
from . import _utils, post


class PostEncoder(json.JSONEncoder):
    """Encode a post.Post object to JSON.

    Inherits from ``json.JSONEncoder``.
    """

    def default(self, o):
        if isinstance(o, post.Post):
            return dataclasses.asdict(o)
        if _utils.is_aware_datetime(o):
            time_in_utc = o.astimezone(datetime.timezone.utc)
            return time_in_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
        return super().default(o)


def _dict_to_post(post_dict):
    """Convert dictionary to post.Post.

    Converts a dictionary representing a post to a real post.Post
    object. Mainly useful for deserialization.

    Parameter
    ---------
    post_dict : dict
        A dictionary whose keys are post.Post attribute names and whose
        values valid post.Post attribute values.

    Returns
    -------
    post : post.Post
        The post object corresponding to the inputted dictionary.
    """
    if 'publish_date' not in post_dict.keys():
        # not the object I'm looking for
        return post_dict

    # Parse datetimes
    post_dict['publish_date'] = dateutil.parser.isoparse(
        post_dict['publish_date'])
    if post_dict['edit_date'] is not None:
        post_dict['edit_date'] = dateutil.parser.isoparse(
            post_dict['edit_date'])
    return post.Post(**post_dict)


class PostDecoder(json.JSONDecoder):
    """Decode a post.Post object from JSON.

    Inherits from ``json.JSONDecoder``, implementing a special hook to
    deserialize post.Post objects.
    """

    def __init__(self, *args, **kwargs):
        """Initialise a PostDecoder object.

        Parameters
        ----------
        *args : tuple
            Additional positional arguments to be passed to
            json.JSONDecoder
        **kwargs : dict
            Additional keyword arguments to be passed to
            json.JSONDecoder
        """
        super().__init__(object_hook=_dict_to_post, *args, **kwargs)
