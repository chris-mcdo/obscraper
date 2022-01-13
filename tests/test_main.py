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

    @unittest.skipUnless(sys.platform.startswith("win"), "windows only")
    def test_invalid_cmd_arguments_raise_errors(self):
        program_call = [r'.\.venv\Scripts\python.exe', '-m', 'obscraper']

        no_options = ['-o', 'outfile.json']
        result = subprocess.run(program_call + no_options)
        self.assertEqual(result.returncode, 2)

        all_with_strings = ['-a', 'url1', 'url2']
        result = subprocess.run(program_call + all_with_strings)
        self.assertEqual(result.returncode, 2)

        dates_with_urls = [
            '-d',
            'https://a.b.c/2021/05/str13.com', 'https://a.b.c/2017/01/str2.com']
        result = subprocess.run(program_call + dates_with_urls)
        self.assertEqual(result.returncode, 2)

        urls_with_nothing = ['-u']
        result = subprocess.run(program_call + urls_with_nothing)
        self.assertEqual(result.returncode, 2)

    def test_core_returns_expected_result_for_urls(self):
        mock_writer = mock_open()
        with patch('obscraper.__main__.open', mock_writer):
            __main__.core(
                ['url1', 'url2'], None, False, 'outfile.json')
        self.mocks['urls'].assert_called_once()
        mock_writer.assert_called_once_with(
            file='outfile.json', mode='w', encoding='utf-8')
        output_string = ''.join([call.args[0].strip()
                                for call in mock_writer().write.call_args_list])
        self.assertEqual(output_string, '[{"url":"urls","post":"urls"}]')

    def test_core_returns_expected_result_for_dates(self):
        mock_writer = mock_open()
        dates = [
            datetime.datetime(2015, 8, 26, tzinfo=datetime.timezone.utc),
            datetime.datetime(2020, 11, 3, tzinfo=datetime.timezone.utc)
        ]
        with patch('obscraper.__main__.open', mock_writer):
            __main__.core((), dates, False, 'outfile.json')
        self.mocks['dates'].assert_called_once()
        mock_writer.assert_called_once_with(
            file='outfile.json', mode='w', encoding='utf-8')
        output_string = ''.join([call.args[0].strip()
                                for call in mock_writer().write.call_args_list])
        self.assertEqual(output_string, '[{"url":"dates","post":"dates"}]')

    def test_core_returns_expected_result_for_all(self):
        mock_writer = mock_open()
        with patch('obscraper.__main__.open', mock_writer):
            __main__.core((), None, True, 'outfile.json')
        self.mocks['all'].assert_called_once()
        mock_writer.assert_called_once_with(
            file='outfile.json', mode='w', encoding='utf-8')
        output_string = ''.join([call.args[0].strip()
                                for call in mock_writer().write.call_args_list])
        self.assertEqual(output_string, '[{"url":"all","post":"all"}]')
