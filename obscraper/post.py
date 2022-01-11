"""Store information from a single overcomingbias post."""

import datetime
import dataclasses
from typing import Dict
from . import extract_post, grab


def create_post(post_html, votes=True, comments=True):
    """Populate a post object using its HTML.

    Initialises post with all attributes except `edit_date`, which must
    be attached afterwards.

    Parameters
    ----------
    post_html : bs4.BeautifulSoup
        Full HTML of an overcomingbias post page.
    votes : bool
        Whether to collect the vote count when creating the post.
    comments : bool
        Whether to collect the comment count when creating the post.

    Returns
    -------
    new_post : Post
        Post initialised from the inputted HTML. Includes vote and
        comment counts (if the `vote` and `comment` flags are set to
        True), but does not `edit_date`.
    """
    new_post = Post(
        # URL and title
        url=extract_post.extract_url(post_html),
        name=extract_post.extract_name(post_html),
        # Metadata
        number=extract_post.extract_number(post_html),
        page_type=extract_post.extract_page_type(post_html),
        page_status=extract_post.extract_page_status(post_html),
        page_format=extract_post.extract_page_format(post_html),
        # Tags and categories
        tags=extract_post.extract_tags(post_html),
        categories=extract_post.extract_categories(post_html),
        # Title, author, date
        title=extract_post.extract_title(post_html),
        author=extract_post.extract_author(post_html),
        publish_date=extract_post.extract_publish_date(post_html),
        # Word count and links
        text_html=extract_post.extract_text_html(post_html),
        word_count=extract_post.extract_word_count(post_html),
        internal_links=extract_post.extract_internal_links(post_html),
        external_links=extract_post.extract_external_links(post_html),
        # Disqus ID string
        disqus_id=extract_post.extract_disqus_id(post_html),
    )
    if votes:
        new_post.votes = grab.grab_votes(new_post.number)
    if comments:
        new_post.comments = grab.grab_comments(new_post.disqus_id)
    return new_post


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
    tags : list[str]
        A list of tags associated with the post.
    categories : list[str]
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
    votes : int
        The number of votes the post has received.
    comments : int
        The number of comments on the post.
    edit_date : datetime.datetime
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
    tags: list[str]
    categories: list[str]
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
        return extract_post.convert_to_plaintext(self.text_html)
