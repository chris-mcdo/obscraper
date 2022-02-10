import json

import pytest

from examples import STANDARD_EXAMPLES
from obscraper import _post, _serialize


@pytest.mark.parametrize("name", STANDARD_EXAMPLES.keys())
def test_encode_and_decode_work_with_standard_examples(standard_examples, name):
    example_post = standard_examples[name]

    encoded = json.dumps(example_post, cls=_serialize.PostEncoder)
    assert isinstance(encoded, str)
    assert encoded != ""

    decoded = json.loads(encoded, cls=_serialize.PostDecoder)
    assert isinstance(decoded, _post.Post)
    assert decoded == example_post


def test_encode_and_decode_work_for_none_post():
    example_post = None

    encoded = json.dumps(example_post, cls=_serialize.PostEncoder)
    assert isinstance(encoded, str)
    assert encoded != ""

    decoded = json.loads(encoded, cls=_serialize.PostDecoder)
    assert decoded is None
