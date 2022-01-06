"""Store information from a single overcomingbias post."""

from . import extract_page, extract_post, grab

def create_post(post_html, votes=False, comments=False):
    """Populate a post object using its HTML."""
    p = Post(
        # URL and title
        url=extract_post.extract_url(post_html),
        name = extract_post.extract_name(post_html),
        # Metadata
        number = extract_post.extract_number(post_html),
        type = extract_post.extract_type(post_html),
        status = extract_post.extract_status(post_html),
        format = extract_post.extract_format(post_html),
        # Tags and categories
        tags = extract_post.extract_tags(post_html),
        categories = extract_post.extract_categories(post_html),
        # Title, author, date
        title = extract_post.extract_title(post_html),
        author = extract_post.extract_author(post_html),
        publish_date = extract_post.extract_publish_date(post_html),
        has_moved=extract_page.has_post_moved(post_html),
        )
    if votes:
        p.set_votes(grab.grab_votes(p.number))
    if comments:
        p.set_comments(grab.grab_comments(p.number))
    # Detailed info (requires full text)
    if not extract_page.is_post_truncated(post_html):
        # Word count and links
        p.set_words_and_links(
            words = extract_post.extract_word_count(post_html),
            internal_links = extract_post.extract_internal_links(post_html),
            external_links = extract_post.extract_external_links(post_html),
        )
    return p

class Post:
    """Class representing a single post.
    
    Attributes:
        url: String. The URL of the post.
        name: String. The original name of the post found in its url, e.g. 
        'jobs-explain-lots'.
        number: Integer. The unique integer identifier of the post.
        type: String. Post type. Can be post (for a normal post), or page (for
        e.g. the Bio page or privacy policy). I don't know its exact definition.
        status: String. Post status. I have only seen 'publish'. But I don't 
        know its exact definition. 
        format: String. I have only seen 'standard'. Not present for non-post 
        pages (e.g. Bio, privacy policy). I don't know its exact definition.
        title: String. The title of the post, as seen on the page. E.g. 'Jobs Explain Lots'.
        author: String. The author of the post.
        publish_date: String. The time when the post was first published, according to the page.
        has_moved: Boolean. Whether the full post is accessible on the overcomingbias site.
        votes: Integer. The number of votes the post has received.
        comments: Integer. The number of comments on the post.
        tags: List (string). A list of tags associated with the post.
        words: Integer. The number of words in the body of the post. Only 
        available for posts which have not moved to other sites.
        internal_links: Dict (string, integer). A dictionary of links to the OB site (and the 
        number of times they're repeated), contained in the body of the post.
        external_links: Dict (string, integer). A list of links to pages outside the OB site
        (and the number of times they're repeated), contained in the body of the post.
        edit_date: String. The time when the post was last edited, according to the sitemap. 
    """
    
    def __init__(self, url, name, number, type, status, format, tags, categories, title, author, publish_date, has_moved):
        """Initialise a Post object."""
        self.url = url
        self.name = name
        self.number = number
        self.type = type
        self.status = status
        self.format = format
        self.tags = tags
        self.categories = categories
        self.title = title
        self.author = author
        self.publish_date = publish_date
        self.has_moved = has_moved        

    def set_votes(self, votes):
        """Add or update vote count."""
        self.votes = votes

    def set_comments(self, comments):
        """Add or update comment count."""
        self.comments = comments
    
    def set_words_and_links(self, words, internal_links, external_links):
        """Add or update word count and hyperlinks."""
        self.words = words
        self.internal_links = internal_links
        self.external_links = external_links

    def set_edit_date(self, edit_date):
        """Add or update "last modified" date."""
        self.edit_date = edit_date