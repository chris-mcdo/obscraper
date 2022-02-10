import re

from obscraper import _assemble


async def test_extract_auth_code_returns_result_in_correct_format(async_http_client):
    vote_auth = await _assemble.assemble_vote_auth(async_http_client)
    assert isinstance(vote_auth, str)
    assert re.search(r"^[a-z0-9]{10}$", vote_auth) is not None
