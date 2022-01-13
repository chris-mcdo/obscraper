

import unittest
from unittest.mock import MagicMock

import datetime

from obscraper import _extract_dates


class TestDateParsing(unittest.TestCase):
    def test_extract_edit_dates_parses_dates_as_expected(self):
        utc = datetime.timezone.utc
        test_dates = {
            '2007-10-04T10:00:00Z': datetime.datetime(2007, 10, 4, 10, 0, 0, tzinfo=utc),
            '2010-12-31T01:32:58Z': datetime.datetime(2010, 12, 31, 1, 32, 58, tzinfo=utc),
            '2010-01-21T13:39:47Z': datetime.datetime(2010, 1, 21, 13, 39, 47, tzinfo=utc),
        }
        mock_xml = MagicMock()
        mock_xml.find_all.return_value = [
            MagicMock(string=raw_date) for raw_date in test_dates.keys()]
        result = _extract_dates.extract_edit_dates(mock_xml)
        self.assertEqual(result, list(test_dates.values()))
