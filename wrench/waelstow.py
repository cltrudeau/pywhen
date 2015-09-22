# wrench.waelstow.py
from unittest import TestCase

def list_tests(suites):
    """Takes a list of suites and returns an iterable of all the tests in
    the suites and their children.

    :param suites:
        A single or an interable of :class:`TestSuite` objects whose contents
        will be listed
    :returns:
        Iterable of :class:`TestCase` objects contained within the suites
    """
    for test in suites:
        if test.__class__.__name__ == 'ModuleImportFailure':
            # ignore the import fail module
            pass
        elif isinstance(test, TestCase):
            yield test
        else:
            for t in list_tests(test):
                yield t


def find_shortcut_tests(suites, shortcut_labels):
    """Takes a suite of tests and returns a list of tests that conform to the
    passed in list of short-cut labels.  A short-cut label begins with an "="
    and is then checked against the full test case and method name, if the
    shortcut string is in the full test name then the test is returned.

    Example:

    .. code-block::python

    >>> list_tests(suite)
    [
        test_foo (wrench.test.SomeTest),
        test_foo (wrench.test.AnotherTest),
        test_bar (wrench.test.AnotherTest),
        test_bar (wrench.test.DifferentTest),
    ]
    >>> find_shorcut_tests(suite, ['=foo'])
    [
        test_foo (wrench.test.SomeTest),
        test_foo (wrench.test.AnotherTest),
    ]
    >>> find_shorcut_tests(suite, ['=Another'])
    [
        test_foo (wrench.test.AnotherTest),
        test_bar (wrench.test.AnotherTest),
    ]

    :param suites:
        A single or iterable of :class:`TestSuite` objects to create the test
        subset from
    :param shortcut_labels:
        A list of short-cut labels to use to cull the list
    :returns:
        A list of :class:`TestCase` objects 
    """
    # strip the '=' from the front of each label
    labels = [label[1:] for label in shortcut_labels]

    results = []
    for test in list_tests(suites):
        name = '%s.%s.%s' % (test.__module__, test.__class__.__name__,
            test._testMethodName)
        for label in labels:
            if label in name:
                results.append(test)

    return results
