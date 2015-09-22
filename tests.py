import unittest, sys

if len(sys.argv[1:]) > 0:
    labels = sys.argv[1:]
    suite = unittest.TestLoader().loadTestsFromNames(labels)
else:
    suite = unittest.TestLoader().discover('wrench')


#from wrench.waelstow import list_tests
#for t in list_tests(suite):
#    print(t)
#
#quit()

unittest.TextTestRunner(verbosity=2).run(suite)
