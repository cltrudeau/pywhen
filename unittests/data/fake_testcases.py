from unittest import TestCase, TestSuite, defaultTestLoader

class ATestCase(TestCase):
    def test_common(self):
        pass

    def test_a(self):
        pass

class BTestCase(TestCase):
    def test_common(self):
        pass

    def test_b(self):
        pass

class CTestCase(TestCase):
    def test_common(self):
        pass
