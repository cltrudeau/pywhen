from datetime import datetime, date, time
from unittest import TestCase

from wrench.utils import When

# =============================================================================

class TestWhen(TestCase):
    def setUp(self):
        self.full_date = datetime(1972, 1, 31, 13, 55)
        self.zero_date = datetime(1972, 1, 31, 0, 0)
        self.only_time = time(13, 55)
        self.epoch = 65732100
        self.mepoch = self.epoch * 1000
        self.micro_epoch = '%s.0000' % (self.epoch)

    def test_constructor(self):
        self.assertEqual(self.full_date, When(datetime=self.full_date).datetime)
        self.assertEqual(self.full_date, 
            When(date=date(1972, 1, 31), time=time(13, 55)).datetime)
        self.assertEqual(self.full_date, 
            When(date=date(1972, 1, 31), time_string='13:55').datetime)
        self.assertEqual(self.full_date, 
            When(date=date(1972, 1, 31), time_string='13:55:00').datetime)

        self.assertEqual(self.full_date, When(epoch=self.epoch).datetime)
        self.assertEqual(self.full_date, When(milli_epoch=self.mepoch).datetime)

        # default time
        self.assertEqual(self.zero_date, When(date=date(1972, 1, 31)).datetime)

        # time only
        self.assertEqual(self.only_time, When(time=time(13, 55)).time)
        self.assertEqual(self.only_time, When(time_string='13:55').time)

        # parse detection
        self.assertEqual(self.zero_date, When(detect='1972-01-31').datetime)
        self.assertEqual(self.only_time, When(detect='13:55').time)
        self.assertEqual(self.only_time, When(detect='13:55:00').time)
        self.assertEqual(self.full_date, 
            When(detect='1972-01-31 13:55').datetime)
        self.assertEqual(self.full_date, 
            When(detect='1972-01-31 13:55:00').datetime)
        self.assertEqual(self.full_date, 
            When(detect='1972-01-31T13:55Z').datetime)
        self.assertEqual(self.full_date, 
            When(detect='1972-01-31T13:55:00Z').datetime)
        self.assertEqual(self.full_date, 
            When(detect='1972-01-31T13:55:00.00Z').datetime)

        # parse force
        self.assertEqual(self.zero_date, When(parse_date='1972-01-31').datetime)
        self.assertEqual(self.only_time, When(parse_time='13:55').time)
        self.assertEqual(self.only_time, When(parse_time_sec='13:55:00').time)
        self.assertEqual(self.full_date, 
            When(parse_datetime='1972-01-31 13:55').datetime)
        self.assertEqual(self.full_date, 
            When(parse_datetime_sec='1972-01-31 13:55:00').datetime)
        self.assertEqual(self.full_date, 
            When(parse_datetime_utc='1972-01-31T13:55Z').datetime)
        self.assertEqual(self.full_date, 
            When(parse_datetime_sec_utc='1972-01-31T13:55:00Z').datetime)
        self.assertEqual(self.full_date, 
            When(parse_iso_micro='1972-01-31T13:55:00.00Z').datetime)

        # check errors
        with self.assertRaises(ValueError):
            When(detect='abc')

        with self.assertRaises(ValueError):
            When(parse_date='abc')

        with self.assertRaises(ValueError):
            When(parse_time='abc')

        with self.assertRaises(ValueError):
            When(parse_time_sec='abc')

        with self.assertRaises(ValueError):
            When(parse_datetime='abc')

        with self.assertRaises(ValueError):
            When(parse_datetime_sec='abc')

        with self.assertRaises(ValueError):
            When(parse_datetime_utc='abc')

        with self.assertRaises(ValueError):
            When(parse_datetime_sec_utc='abc')

        with self.assertRaises(ValueError):
            When(parse_iso_micro='abc')

        with self.assertRaises(AttributeError):
            When()

    def test_values(self):
        when = When(datetime=self.full_date)

        self.assertEqual('1972-01-31', when.string.date)
        self.assertEqual('13:55', when.string.time)
        self.assertEqual('13:55:00', when.string.time_sec)
        self.assertEqual('1972-01-31 13:55', when.string.datetime)
        self.assertEqual('1972-01-31 13:55:00', when.string.datetime_sec)
        self.assertEqual('1972-01-31T13:55Z', when.string.datetime_utc)
        self.assertEqual('1972-01-31T13:55:00Z', when.string.datetime_sec_utc)
        self.assertEqual('1972-01-31T13:55:00.0Z', when.string.iso_micro)

        self.assertEqual(self.full_date, when.datetime)
        self.assertEqual(self.full_date.date(), when.date)
        self.assertEqual(self.only_time, when.time)
        self.assertEqual(self.epoch, when.epoch)
        self.assertEqual(self.mepoch, when.milli_epoch)
