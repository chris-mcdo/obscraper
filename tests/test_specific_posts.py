import pytest
from utils import assert_is_valid_post

from examples import INVALID_SPECIAL_CASES, STANDARD_EXAMPLES, VALID_SPECIAL_CASES
from obscraper._extract_post import name_to_url


@pytest.mark.parametrize("name", STANDARD_EXAMPLES.keys())
def test_standard_examples_have_expected_attributes(standard_examples, name):
    test_input = standard_examples[name]
    expected = STANDARD_EXAMPLES[name]
    assert test_input.name == name
    assert test_input.url == name_to_url(name)
    assert test_input.title == expected["title"]
    assert test_input.author == expected["author"]
    assert test_input.publish_date == expected["publish_date"]
    assert test_input.number == expected["number"]
    assert test_input.tags == expected["tags"]
    assert test_input.categories == expected["categories"]
    assert test_input.page_type == "post"
    assert test_input.page_status == "publish"
    assert test_input.page_format == "standard"
    assert test_input.plaintext.endswith(expected["endswith"])
    assert test_input.word_count == expected["word_count"]
    if expected["external_links"] is not None:
        assert sorted(test_input.external_links) == sorted(expected["external_links"])
    assert sorted(test_input.internal_links) == sorted(expected["internal_links"])
    assert test_input.disqus_id == expected["disqus_id"]


def test_returns_expected_results_for_special_cases(special_cases):
    for case in VALID_SPECIAL_CASES:
        assert_is_valid_post(special_cases[case])

    for case in INVALID_SPECIAL_CASES:
        assert special_cases[case] is None
