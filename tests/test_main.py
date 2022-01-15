import subprocess
import sys
import datetime
import unittest
from unittest.mock import patch, mock_open

from obscraper import __main__


class TestMain(unittest.TestCase):

    def setUp(self):
        # remove all patches once complete
        self.addCleanup(patch.stopall)
        # patch all scrape functions
        self.patchers = {
            'all': patch('obscraper._scrape.get_all_posts', return_value={'all': 'all'}),
            'urls': patch('obscraper._scrape.get_posts_by_urls', return_value={'urls': 'urls'}),
            'dates': patch('obscraper._scrape.get_posts_by_edit_date', return_value={'dates': 'dates'})
        }
        self.mocks = {key: patcher.start()
                      for key, patcher in self.patchers.items()}

    def test_main_returns_expected_result_for_urls(self):
        mock_writer = mock_open()
        with patch('obscraper.__main__.open', mock_writer):
            try:
                __main__.main(['-u', 'url1', 'url2', '-o', 'outfile.json'])
            except SystemExit as sysexit:
                self.assertEqual(sysexit.code, 0)
                self.mocks['urls'].assert_called_once()
                mock_writer.assert_called_once_with(
                    file='outfile.json', mode='w', encoding='utf-8')
                output_string = ''.join([call.args[0].strip()
                                        for call in mock_writer().write.call_args_list])
                self.assertEqual(
                    output_string, '[{"url":"urls","post":"urls"}]')

    def test_main_returns_expected_result_for_dates(self):
        mock_writer = mock_open()
        dates = [
            "26th August 2015",
            "18th January 2019",
        ]
        with patch('obscraper.__main__.open', mock_writer):
            try:
                __main__.main(['-d'] + dates + ['-o', 'outfile.json'])
            except SystemExit as sysexit:
                self.assertEqual(sysexit.code, 0)
                self.mocks['dates'].assert_called_once()
                mock_writer.assert_called_once_with(
                    file='outfile.json', mode='w', encoding='utf-8')
                output_string = ''.join([call.args[0].strip()
                                        for call in mock_writer().write.call_args_list])
                self.assertEqual(
                    output_string, '[{"url":"dates","post":"dates"}]')

    def test_main_returns_expected_result_for_all(self):
        mock_writer = mock_open()
        with patch('obscraper.__main__.open', mock_writer):
            try:
                __main__.main(['-a', '-o', 'outfile.json'])
            except SystemExit as sysexit:
                self.assertEqual(sysexit.code, 0)
                self.mocks['all'].assert_called_once()
                mock_writer.assert_called_once_with(
                    file='outfile.json', mode='w', encoding='utf-8')
                output_string = ''.join([call.args[0].strip()
                                        for call in mock_writer().write.call_args_list])
                self.assertEqual(output_string, '[{"url":"all","post":"all"}]')
