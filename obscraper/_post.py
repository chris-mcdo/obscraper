"""Store information from a single overcomingbias post."""

import dataclasses
import datetime
from typing import List

from . import _extract_post


@dataclasses.dataclass(order=False)
class Post:
    """Class representing a single post.

    Attributes
    ----------
    name : str
        The original year, month and abbreviated name of the post, as found in its url.
        E.g. '/2010/09/jobs-explain-lots'.
    number : int
        The unique integer identifier of the post.
    page_type : str
        Page type, normally 'post'. I don't know its definition.
    page_status : str
        Page status, normally 'publish'. I don't know its definition.
    page_format : str
        Page format, normally 'standard'. I don't know its definition.
    title : str
        The title of the post, as seen on the page. E.g. 'Jobs Explain Lots'.
    author : str
        The name of the author of the post. E.g. 'Robin Hanson'
    publish_date : datetime.datetime
        The (aware) datetime when the post was first published, according to the post
        page.
    tags : List[str]
        A list of tags associated with the post.
    categories : List[str]
        A list of categories associated with the post.
    text_html : str
        The full text of the post in HTML format.
    word_count : int
        The number of words in the body of the post.
    internal_links : List[str]
        List of hyperlinks to other posts. May contain duplicates.
    external_links : List[str]
        List of hyperlinks to external webpages. May contain duplicates.
    disqus_id : str
        A string which uniquely identifies the post to the Disqus comment count API.
    votes : int, optional
        The number of votes the post has received.
    comments : int, optional
        The number of comments on the post.
    edit_date : datetime.datetime, optional
        The (aware) datetime when the post was last edited, according to the sitemap.
    """

    # pylint: disable=too-many-instance-attributes
    name: str
    number: int
    page_type: str
    page_status: str
    page_format: str
    title: str
    author: str
    publish_date: datetime.datetime
    tags: List[str]
    categories: List[str]
    text_html: str
    word_count: int
    internal_links: List[str]
    external_links: List[str]
    disqus_id: str
    votes: int = None
    comments: int = None
    edit_date: datetime.datetime = None

    @property
    def url(self):
        """str : The URL of the post."""
        return _extract_post.name_to_url(self.name)

    @property
    def plaintext(self):
        """str : The full text of the post in plaintext format."""
        return _extract_post.convert_to_plaintext(self.text_html)
