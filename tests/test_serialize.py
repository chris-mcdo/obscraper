import unittest

import json

from obscraper import _grab, _post, _scrape, _serialize


class TestSerialize(unittest.TestCase):

    def test_encode_and_decode_work_with_test_post(self):
        pass
        # post_name = '/2006/11/introduction'
        # example_post = _scrape.get_posts_by_names(post_name)[post_name]

        # encoded = json.dumps(example_post, cls=_serialize.PostEncoder)
        # self.assertIsInstance(encoded, str)
        # self.assertNotEqual(encoded, '')

        # decoded = json.loads(encoded, cls=_serialize.PostDecoder)
        # self.assertIsInstance(decoded, _post.Post)
        # self.assertEqual(decoded, example_post)

    def test_encode_and_decode_work_without_edit_date(self):
        example_post = _grab.grab_post_by_name('/2006/11/introduction')

        encoded = json.dumps(example_post, cls=_serialize.PostEncoder)
        self.assertIsInstance(encoded, str)
        self.assertNotEqual(encoded, '')

        decoded = json.loads(encoded, cls=_serialize.PostDecoder)
        self.assertIsInstance(decoded, _post.Post)
        self.assertEqual(decoded, example_post)

    def test_encode_and_decode_work_for_none_post(self):
        example_post = None

        encoded = json.dumps(example_post, cls=_serialize.PostEncoder)
        self.assertIsInstance(encoded, str)
        self.assertNotEqual(encoded, '')

        decoded = json.loads(encoded, cls=_serialize.PostDecoder)
        self.assertIsNone(decoded)
