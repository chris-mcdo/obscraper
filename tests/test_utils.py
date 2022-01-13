
import unittest
from unittest.mock import patch

import datetime

from obscraper import _utils


class TestDateTidying(unittest.TestCase):
    def test_date_functions_return_aware_datetime_objects(self):
        example_date = _utils.tidy_date(
            'July 11, 2011 9:00 am', 'Europe/London')
        self.assertIsInstance(example_date, datetime.datetime)
        self.assertIsNotNone(example_date.tzinfo)
        self.assertIsNotNone(example_date.tzinfo.utcoffset(example_date))

    def test_tidy_date_works_with_different_timezones(self):
        tidy_date = _utils.tidy_date
        utc = datetime.timezone.utc
        # UK winter
        self.assertEqual(tidy_date('March 29, 2019 9:00 am', 'Europe/London'),
                         datetime.datetime(2019, 3, 29, 9, tzinfo=utc))
        # UK summer
        self.assertEqual(tidy_date('March 28, 2021 9:00 am', 'Europe/London'),
                         datetime.datetime(2021, 3, 28, 8, tzinfo=utc))
        # US winter
        self.assertEqual(tidy_date('December 25, 2013 1:00 pm', 'Europe/London'),
                         datetime.datetime(2013, 12, 25, 13, tzinfo=utc))
        # US winter
        self.assertEqual(tidy_date('March 12, 2021 3:00 pm', 'US/Eastern'),
                         datetime.datetime(2021, 3, 12, 20, tzinfo=utc))
        # US summer
        self.assertEqual(tidy_date('March 9, 2015 9:00 pm', 'US/Eastern'),
                         datetime.datetime(2015, 3, 10, 1, tzinfo=utc))

    def test_is_aware_datetime_works_as_expected(self):
        # TODO
        # Practically copied and pasted from python docs, so not too critical
        pass


class TestCountWords(unittest.TestCase):
    def test_count_words_works_for_example_strings(self):
        count = _utils.count_words
        self.assertEqual(count('Two words'), 2)
        self.assertEqual(
            count('... lots; of puncation -- and some weird!? unicode @~¯\_(ツ)_/¯'), 7)
        self.assertEqual(count('Text with\nLine Breaks'), 4)
        self.assertEqual(count(''), 0)
        self.assertEqual(count(r'@@`]` ][[];[, ;..,``\/\/'), 0)
        self.assertEqual(count('2 numbers 2s'), 3)
        self.assertEqual(count('hyphenated-words are counted as-one'), 4)
        self.assertEqual(count('email@adress.com is one word'), 4)
