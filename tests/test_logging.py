from unittest.mock import Mock, patch

import pytest

import obscraper


@pytest.fixture
def mock_assemble_post():
    async def fake_assemble_post(async_client, name):
        if name == "/2020/01/raise-invalid-response":
            raise obscraper.InvalidResponseError
        elif name == "/2020/01/raise-attribute-not-found":
            raise obscraper.AttributeNotFoundError
        else:
            return "Fake Post"

    return Mock(side_effect=fake_assemble_post)


def test_successful_grab_is_logged_as_expected(mock_assemble_post, logs):
    name = "/2020/01/fake-post"
    with patch("obscraper._assemble.assemble_post", mock_assemble_post):
        result = obscraper.get_post_by_name(name)
    assert result == "Fake Post"
    assert logs.getvalue() == f"INFO Successfully grabbed post {name}\n"


def test_invalid_response_is_logged_as_expected(mock_assemble_post, logs):
    name = "/2020/01/raise-invalid-response"
    with patch("obscraper._assemble.assemble_post", mock_assemble_post):
        with pytest.raises(obscraper.InvalidResponseError):
            obscraper.get_post_by_name(name)
    assert (
        logs.getvalue()
        == f"INFO InvalidResponseError raised when grabbing post {name}\n"
    )


def test_attribute_not_found_is_logged_as_expected(mock_assemble_post, logs):
    name = "/2020/01/raise-attribute-not-found"
    with patch("obscraper._assemble.assemble_post", mock_assemble_post):
        with pytest.raises(obscraper.InvalidResponseError):
            obscraper.get_post_by_name(name)
    assert (
        logs.getvalue()
        == f"WARNING AttributeNotFoundError raised when grabbing post {name}\n"
    )
