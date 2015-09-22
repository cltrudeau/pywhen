import os, shutil, tempfile
from unittest import TestCase

from wrench.utils import temp_directory, replaced_directory

# =============================================================================

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
