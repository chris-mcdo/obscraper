"""Store information from a single overcomingbias post."""

import datetime
import dataclasses
from typing import Dict, List
from . import _extract_post


@dataclasses.dataclass(order=False)
class Post:
    """Class representing a single post.

    Attributes
    ----------
    url : str
        The URL of the post.
    name : str
        The original name of the post found in its url, e.g.
        'jobs-explain-lots'.
    number : int
        The unique integer identifier of the post.
    page_type : str
        Page type, normally 'post'. I don't know its definition.
    page_status : str
        Page status, normally 'publish'. I don't know its definition.
    page_format : str
        Page format, normally 'standard'. I don't know its definition.
    title : str
        The title of the post, as seen on the page. E.g. 'Jobs Explain
        Lots'.
    author : str
        The name of the author of the post. E.g. 'Robin Hanson'
    publish_date : datetime.datetime
        The (aware) datetime when the post was first published,
        according to the post page.
    tags : List[str]
        A list of tags associated with the post.
    categories : List[str]
        A list of categories associated with the post.
    text_html : str
        The full text of the post in HTML format.
    word_count : int
        The number of words in the body of the post.
    internal_links : Dict[str, int]
        Dictionary whose keys are the hyperlinks to other posts found in
        the body of the post (str), and whose values are the number of
        times these links are repeated (int).
    external_links : Dict[str, int]
        Dictionary whose keys are the hyperlinks to non-post webpages
        found in the body of the post (str), and whose values are
        the number of times these links are repeated (int).
    disqus_id : str
        A string which uniquely identifies the post to the Disqus
        comment count API.
    votes : int, optional
        The number of votes the post has received.
    comments : int, optional
        The number of comments on the post.
    edit_date : datetime.datetime, optional
        The (aware) datetime when the post was last edited, according to
        the sitemap.
    """
    # pylint: disable=too-many-instance-attributes
    url: str
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
    internal_links: Dict[str, int]
    external_links: Dict[str, int]
    disqus_id: str
    votes: int = None
    comments: int = None
    edit_date: datetime.datetime = None

    @property
    def plaintext(self) -> str:
        """Get post text as plaintext."""
        return _extract_post.convert_to_plaintext(self.text_html)
