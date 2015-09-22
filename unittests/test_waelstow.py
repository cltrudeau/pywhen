import os
from unittest import TestCase, TestSuite, defaultTestLoader

from wrench.waelstow import list_tests, find_shortcut_tests, discover_tests

# =============================================================================

class WaelstowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        current = os.path.dirname(__file__)
        cls.start_dir = os.path.abspath(os.path.join(current, 'data'))
        cls.pattern = 'fake_testcases.py'

        cls.all_cases = {
            'ac':'test_common (fake_testcases.ATestCase)',
            'aa':'test_a (fake_testcases.ATestCase)',
            'bc':'test_common (fake_testcases.BTestCase)',
            'bb':'test_b (fake_testcases.BTestCase)',
            'cc':'test_common (fake_testcases.CTestCase)',
        }

    def _get_expected(self, names):
        keys = names.split(',')
        return [self.all_cases[key] for key in keys]

    def _get_suite_groupings(self):
        suite = discover_tests(self.start_dir, labels=['=ATest'], 
            pattern=self.pattern)
        group = TestSuite(suite)
        suite = discover_tests(self.start_dir, labels=['=BTest'], 
            pattern=self.pattern)
        group.addTests(suite)

        suite = discover_tests(self.start_dir, labels=['=CTest'], 
            pattern=self.pattern)
        return TestSuite([suite, group])

    def assert_test_strings(self, expected, tests):
        expected_names = self._get_expected(expected)
        names = [str(test) for test in tests]
        self.assertEqual(set(expected_names), set(names))

    def test_list_tests(self):
        class ModuleImportFailure(TestSuite):
            pass

        # get out test suite and add in our mock of python's failure module to
        # make sure list_tests skips it
        suite = self._get_suite_groupings()
        suite.addTest(ModuleImportFailure())

        tests = list(list_tests(suite))
        self.assert_test_strings('aa,ac,bb,bc,cc', tests)

    def _check_discover(self, labels, expected):
        suite = discover_tests(self.start_dir, labels=labels, 
            pattern=self.pattern)
        tests = list_tests(suite)
        self.assert_test_strings(expected, tests)

    def test_discover_and_shortcuts(self):
        # -- find all
        self._check_discover([], 'ac,aa,bc,bb,cc')

        # -- test shortcuts
        labels = ['=common']
        self._check_discover(labels, 'ac,bc,cc')

        labels = ['=_a', '=_b']
        self._check_discover(labels, 'aa,bb')

        labels = ['=ATest']
        self._check_discover(labels, 'aa,ac')

        # -- test full labels
        labels = [
            'fake_testcases.ATestCase.test_a',
            'fake_testcases.BTestCase.test_b',
        ]
        self._check_discover(labels, 'aa,bb')

        # -- test mix
        labels = ['=ATestCase', 'fake_testcases.BTestCase.test_b', ]
        self._check_discover(labels, 'aa,ac,bb')

    def test_misc(self):
        # misc stuff to hit our 100% coverage 
        suite = discover_tests(self.start_dir, pattern=self.pattern)
        for t in list_tests(suite):
            t.run()
