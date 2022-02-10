import datetime

from obscraper import _post, _utils


def test_date_functions_return_aware_datetime_objects():
    example_date = _utils.tidy_date("July 11, 2011 9:00 am", "Europe/London")
    assert isinstance(example_date, datetime.datetime)
    assert example_date.tzinfo is not None
    example_date.tzinfo.utcoffset(example_date) is not None


def test_tidy_date_works_with_different_timezones():
    tidy_date = _utils.tidy_date
    utc = datetime.timezone.utc
    # UK winter
    assert tidy_date("March 29, 2019 9:00 am", "Europe/London") == datetime.datetime(
        2019, 3, 29, 9, tzinfo=utc
    )
    # UK summer
    assert tidy_date("March 28, 2021 9:00 am", "Europe/London") == datetime.datetime(
        2021, 3, 28, 8, tzinfo=utc
    )
    # US winter
    assert tidy_date("December 25, 2013 1:00 pm", "Europe/London") == datetime.datetime(
        2013, 12, 25, 13, tzinfo=utc
    )
    # US winter
    assert tidy_date("March 12, 2021 3:00 pm", "US/Eastern") == datetime.datetime(
        2021, 3, 12, 20, tzinfo=utc
    )
    # US summer
    assert tidy_date("March 9, 2015 9:00 pm", "US/Eastern") == datetime.datetime(
        2015, 3, 10, 1, tzinfo=utc
    )


def test_is_aware_datetime_works_as_expected():
    # TODO
    # Practically copied and pasted from python docs, so not too critical
    pass


def test_count_words_works_for_example_strings():
    count = _utils.count_words
    assert count("Two words") == 2
    assert count(r"... lots; of punctuation -- and unusual!? unicode @~¯\_(ツ)_/¯") == 6
    assert count("Text with\nLine Breaks") == 4
    assert count("") == 0
    assert count(r"@@`]` ][[];[, ;..,``\/\/") == 0
    assert count("2 numbers 2s") == 3
    assert count("hyphenated-words are counted as-one") == 4
    assert count("email@adress.com is one word") == 4
    assert count("ignore some silly words", ignore=["silly"]) == 3


def test_returns_valid_result_for_post():
    assert _utils.property_names(_post.Post) == ["plaintext", "url"]
