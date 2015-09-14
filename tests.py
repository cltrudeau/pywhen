import unittest

suite = unittest.TestLoader().discover('wrench')
unittest.TextTestRunner(verbosity=2).run(suite)
