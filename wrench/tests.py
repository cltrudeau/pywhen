import os, shutil, tempfile
from datetime import datetime, date, time
from unittest import TestCase

from utils import (ExtendedEnum, When, dynamic_load, camelcase_to_underscore,
    rows_to_columns, temp_directory, replaced_directory)

# =============================================================================

class ColourEnum(ExtendedEnum):
    red = 'r'
    blue = 'b'
    green = 'g'


class TestEnum(TestCase):
    def test_enum(self):
        # test choices()
        choices = ColourEnum.choices()
        self.assertEqual(len(choices), 3)
        self.assertIn(('r', 'red'), choices)
        self.assertIn(('b', 'blue'), choices)
        self.assertIn(('g', 'green'), choices)

        # test count()
        self.assertEqual(3, ColourEnum.count())

        # test values()
        values = ColourEnum.values()
        self.assertEqual(len(values), 3)
        self.assertIn('r', values)
        self.assertIn('b', values)
        self.assertIn('g', values)

        # test names()
        names = ColourEnum.names()
        self.assertEqual(len(names), 3)
        self.assertIn('red', names)
        self.assertIn('blue', names)
        self.assertIn('green', names)

        
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


class TestUtils(TestCase):
    def test_dynamic_load(self):
        import os
        fn = dynamic_load('os.path.abspath')
        self.assertEqual(os.path.abspath, fn)

    def test_camelcase(self):
        pairs = [
            ('one', 'one'),
            ('one_two', 'oneTwo'),
            ('one_two', 'OneTwo'),
        ]

        for pair in pairs:
            self.assertEqual(pair[0], camelcase_to_underscore(pair[1]))

    def test_rows_to_cols(self):
        matrix = [ 
            [0, 1, 2],
            [3, 4, 5],
            [6, 7, 8],
        ]

        expected = [ 
            [0, 3, 6],
            [1, 4, 7],
            [2, 5, 8],
        ]

        self.assertEqual(expected, rows_to_columns(matrix))


class TestContexts(TestCase):
    def test_temp_dir(self):
        created_td = ''
        with temp_directory() as td:
            created_td = td
            name = os.path.join(td, 'a.txt')
            with open(name, 'w') as f:
                f.write('foo')

            os.path.isfile(name)

        # verify that the temp directory has been cleaned up
        self.assertFalse(os.path.exists(created_td))

        # -- test failure still cleans up
        try:
            with temp_directory() as td:
                created_td = td
                raise RuntimeError()
        except:
            pass

        self.assertFalse(os.path.exists(created_td))

    def test_replace_dir(self):
        # create a temp directory and put something in it which is to be
        # replaced
        test_dir = tempfile.mkdtemp()
        orig_file = os.path.join(test_dir, 'a.txt')
        replace_file = os.path.join(test_dir, 'b.txt')

        with open(orig_file, 'w') as f:
            f.write('foo')

        # test not a dir handling
        with self.assertRaises(AttributeError):
            # call context manager by hand as putting it in a "with" will
            # result in unreachable code which blows our testing coverage
            rd = replaced_directory(orig_file)
            rd.__enter__()

        # replace_directory should handle trailing slashes
        test_dir += '/'

        created_td = ''
        with replaced_directory(test_dir) as td:
            created_td = td

            # put something in the replaced directory
            with open(replace_file, 'w') as f:
                f.write('bar')

            # original should be moved out of path, replaced should exist
            self.assertFalse(os.path.exists(orig_file))
            self.assertTrue(os.path.exists(replace_file))

        # original should be back, replaced should be gone
        self.assertTrue(os.path.exists(orig_file))
        self.assertFalse(os.path.exists(replace_file))
        self.assertFalse(os.path.exists(created_td))

        # -- test failure still cleans up
        try:
            with replaced_directory(test_dir) as td:
                created_td = td
                raise RuntimeError()
        except:
            pass

        self.assertTrue(os.path.exists(orig_file))
        self.assertFalse(os.path.exists(created_td))

        # -- cleanup testcase
        shutil.rmtree(test_dir)
