"""Encode and decode Post objects."""

import dataclasses
import datetime
import json

import dateutil.parser

from . import _post, _utils


class PostEncoder(json.JSONEncoder):
    """Encode obscraper.Post object to JSON.

    All obscraper.Post attributes and properties (including post
    plaintext and URL) are included in the serialized object.

    Inherits from ``json.JSONEncoder``.
    """

    def default(self, o):
        if isinstance(o, _post.Post):
            attributes = dataclasses.asdict(o)
            properties = {
                name: getattr(o, name) for name in _utils.property_names(_post.Post)
            }
            return {**attributes, **properties}
        if _utils.is_aware_datetime(o):
            time_in_utc = o.astimezone(datetime.timezone.utc)
            return time_in_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
        return super().default(o)


def dict_to_post(post_dict):
    """Convert dictionary to obscraper.Post.

    Converts a dictionary representing a post to a real obscraper.Post
    object. Mainly useful for deserialization.

    Parameters
    ---------
    post_dict : dict
        A dictionary whose keys are obscraper.Post attribute names and
        whose values valid obscraper.Post attribute values.

    Returns
    -------
    obscraper.Post
        The post object corresponding to the inputted dictionary.
    """
    if "publish_date" not in post_dict.keys():
        # not the object I'm looking for
        return post_dict

    # Don't pass properties to the Post constructor
    for name in _utils.property_names(_post.Post):
        post_dict.pop(name, None)

    # Parse datetimes
    post_dict["publish_date"] = dateutil.parser.isoparse(post_dict["publish_date"])
    if post_dict["edit_date"] is not None:
        post_dict["edit_date"] = dateutil.parser.isoparse(post_dict["edit_date"])
    return _post.Post(**post_dict)


class PostDecoder(json.JSONDecoder):
    """Decode a obscraper.Post object from JSON.

    Inherits from ``json.JSONDecoder``, implementing a special
    ``object_hook`` to deserialize obscraper.Post objects.
    """

    def __init__(self):
        super().__init__(object_hook=dict_to_post)
