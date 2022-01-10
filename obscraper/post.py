"""Store information from a single overcomingbias post."""

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
        text=extract_post.extract_text(post_html),
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
    publish_date : aware datetime.datetime
        The datetime when the post was first published, according to the
        post page.
    tags : list of str
        A list of tags associated with the post.
    text : str
        The full text of the post, as plaintext.
    word_count : int
        The number of words in the body of the post.
    internal_links : dict
        Dictionary whose keys are the hyperlinks to other posts found in
        the body of the post (str), and whose values are the number of
        times these links are repeated (int).
    external_links : dict
        Dictionary whose keys are the hyperlinks to non-post webpages
        found in the body of the post (str), and whose values are
        the number of times these links are repeated (int).
    disqus_id : str
        A string which uniquely identifies the post to the Disqus
        comment count API.
    edit_date : aware datetime.datetime
        The datetime when the post was last edited, according to the
        sitemap.
    votes : int
        The number of votes the post has received.
    comments : int
        The number of comments on the post.
    """

    def __init__(self, url, name, number, page_type, page_status, page_format,
                 tags, categories, title, author, publish_date, text,
                 word_count, internal_links, external_links, disqus_id,
                 votes=None, comments=None, edit_date=None):
        """Initialise a Post object."""
        self.url = url
        self.name = name
        self.number = number
        self.page_type = page_type
        self.page_status = page_status
        self.page_format = page_format
        self.tags = tags
        self.categories = categories
        self.title = title
        self.author = author
        self.publish_date = publish_date
        self.text = text
        self.word_count = word_count
        self.internal_links = internal_links
        self.external_links = external_links
        self.disqus_id = disqus_id
        self.votes = votes
        self.comments = comments
        self.edit_date = edit_date
