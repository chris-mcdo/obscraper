from utils import tidy_us_date

from obscraper._extract_post import name_to_url

STANDARD_EXAMPLES = {  # first post
    "/2006/11/introduction": {
        "title": "How To Join",
        "author": "Robin Hanson",
        "publish_date": tidy_us_date("November 20, 2006 6:00 am"),
        "number": 18402,
        "tags": ["meta"],
        "categories": ["meta"],
        "endswith": "Copyright is retained by each author.",
        "word_count": 263,
        "internal_links": [
            "http://www.overcomingbias.com/2006/12/contributors_be.html",
            "http://www.overcomingbias.com/2007/02/moderate_modera.html",
        ],
        "external_links": ["http://www.fhi.ox.ac.uk/"],
        "disqus_id": "18402 http://prod.ob.trike.com.au/2006/11/how-to-join.html",
    },
    # early post by another author
    "/2007/03/the_very_worst_": {
        "title": "The Very Worst Kind of Bias",
        "author": "David J. Balan",
        "publish_date": tidy_us_date("March 26, 2007 8:53 am"),
        "number": 18141,
        "tags": ["morality", "psychology"],
        "categories": ["morality", "psychology"],
        "endswith": "unlikely to correspond to truth.",
        "word_count": 315,
        "internal_links": [],
        "external_links": [
            "http://www.solstice.us/russell/religionciv.html",
            "http://www.davidbrin.com/addiction.html",
        ],
        "disqus_id": "18141"
        " http://prod.ob.trike.com.au/2007/03/the-very-worst-kind-of-bias.html",
    },
    # 2007 post with embedded image
    "/2007/04/as_good_as_it_g": {
        "title": "As Good As It Gets",
        "author": "Robin Hanson",
        "publish_date": tidy_us_date("April 7, 2007 6:00 am"),
        "number": 18115,
        "tags": ["standard-biases"],
        "categories": ["standard-biases"],
        "endswith": "but definitely worth living.",
        "word_count": 155,
        "internal_links": [],
        "external_links": [
            "/wp-content/uploads/2007/04/asgoodasitgets_2.jpg",
        ],
        "disqus_id": "18115"
        " http://prod.ob.trike.com.au/2007/04/as-good-as-it-gets.html",
    },
    # just before Disqus API changes
    "/2009/05/we-only-need-a-handshake": {
        "title": "Just A Handshake",
        "author": "Robin Hanson",
        "publish_date": tidy_us_date("May 26, 2009 2:00 pm"),
        "number": 18423,
        "tags": ["signaling", "social-science"],
        "categories": ["signaling", "social-science"],
        "endswith": "even when backed by such publications.",
        "word_count": 247,
        "internal_links": [],
        "external_links": [
            "http://dx.doi.org/10.1016/j.geb.2009.05.001",
        ],
        "disqus_id": "18423 http://www.overcomingbias.com/?p=18423",
    },
    # old post with embedded video
    "/2013/11/me-on-rt-america-4pm-est-today": {
        "title": "Me on RT America Soon",
        "author": "Robin Hanson",
        "publish_date": tidy_us_date("November 12, 2013 2:20 pm"),
        "number": 30613,
        "tags": ["personal", "social-science"],
        "categories": ["uncategorized"],
        "endswith": "here is the 5 minute video:",
        "word_count": 28,
        "internal_links": [],
        "external_links": [
            "http://rt.com/on-air/rt-america-air/",
        ],
        "disqus_id": "30613 http://www.overcomingbias.com/?p=30613",
    },
    # before Disqus API changes (2nd time)
    "/2021/04/shoulda-listened-futures": {
        "title": "Shoulda-Listened Futures",
        "author": "Robin Hanson",
        "publish_date": tidy_us_date("April 27, 2021 6:45 pm"),
        "number": 32811,
        "tags": ["academia", "prediction-markets", "project"],
        "categories": ["uncategorized"],
        "endswith": "will never be directly evaluated.",
        "word_count": 1205,
        "internal_links": [],
        "external_links": [],
        "disqus_id": "32811 http://www.overcomingbias.com/?p=32811",
    },
    # post with embedded tweet
    "/2021/12/we-dont-have-to-die": {
        "title": "We Don’t Have To Die",
        "author": "Robin Hanson",
        "publish_date": tidy_us_date("December 16, 2021 6:15 pm"),
        "number": 33014,
        "tags": ["future", "medicine"],
        "categories": ["uncategorized"],
        "endswith": "pretty minor issue here.",
        "word_count": 1336,  # likely to change
        "internal_links": [
            name_to_url("/2012/06/frozen-or-plastic-brain"),
            name_to_url("/2010/07/modern-male-sati"),
            name_to_url("/2010/07/space-ashes-vs-cryonics"),
            name_to_url("/2020/01/how-to-not-die-soon"),
            name_to_url("/2020/01/how-to-not-die-soon"),
            name_to_url("/2008/12/tyler-on-cryonics"),
        ],
        "external_links": None,
        "disqus_id": "33014 https://www.overcomingbias.com/?p=33014",
    },
}

VALID_SPECIAL_CASES = [
    r"/2007/01/the-procrastinator%e2%80%99s-clock",  # Unusual name example
]

INVALID_SPECIAL_CASES = [
    "/2007/10/a-rational-argu",  # LessWrong example
    "/2012/08/not-a-real-post",  # Fake example
    "/2009/02/the-most-important-thing",  # Broken post (raises AttributeError)
]

TEST_DISQUS_IDS = {
    18402: "18402 http://prod.ob.trike.com.au/2006/11/how-to-join.html",
    18141: "18141 http://prod.ob.trike.com.au/2007/03/the-very-worst-kind-of-bias.html",
    18115: "18115 http://prod.ob.trike.com.au/2007/04/as-good-as-it-gets.html",
    18423: "18423 http://www.overcomingbias.com/?p=18423",
    30613: "30613 http://www.overcomingbias.com/?p=30613",
    32811: "32811 http://www.overcomingbias.com/?p=32811",
    33014: "33014 https://www.overcomingbias.com/?p=33014",
}
