
from io import StringIO
import unittest
from unittest.mock import patch
import logging

import obscraper


class TestLogging(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Configure logging
        cls.logger = logging.getLogger('obscraper')
        cls.logger.level = logging.DEBUG
        # Set up patches
        def patched_grab(name):
            if name == '/2020/01/raise-invalid-response':
                raise obscraper.InvalidResponseError
            elif name == '/2020/01/raise-attribute-not-found':
                raise obscraper.AttributeNotFoundError
            else:
                return 'Fake Post'
        cls.mock_grab = patch('obscraper._grab.grab_post_by_name', 
                              side_effect=patched_grab).start()
        cls.mock_attach_dates = patch('obscraper._scrape.attach_edit_dates',
                                       lambda v: v).start()
        cls.addClassCleanup(patch.stopall)


    def setUp(self):
        # Save logs to memory
        self.logs = StringIO()
        formatter = logging.Formatter('%(levelname)s %(message)s')
        self.handler = logging.StreamHandler(self.logs)
        self.handler.formatter = formatter
        self.logger.addHandler(self.handler)

    def tearDown(self):
        self.logger.removeHandler(self.handler)

    def test_successful_grab_is_logged_as_expected(self):
        name = '/2020/01/fake-post'
        result = obscraper.get_posts_by_names([name])[name]
        self.assertEqual(result, 'Fake Post')
        self.assertEqual(self.logs.getvalue(),
                         f'INFO Successfully grabbed post {name}\n')

    def test_invalid_response_is_logged_as_expected(self):
        name = '/2020/01/raise-invalid-response'
        result = obscraper.get_posts_by_names([name])[name]
        self.assertIsNone(result)
        self.assertEqual(self.logs.getvalue(),
                         f'INFO InvalidResponseError raised when grabbing post {name}\n')

    def test_attribute_not_found_is_logged_as_expected(self):
        name = '/2020/01/raise-attribute-not-found'
        result = obscraper.get_posts_by_names([name])[name]
        self.assertIsNone(result)
        self.assertEqual(self.logs.getvalue(),
                         f'WARNING AttributeNotFoundError raised when grabbing post {name}\n')
