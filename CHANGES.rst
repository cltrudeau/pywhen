0.7
===

* moved all Context Managers into their own module "contexts"
* added capture_stdout() Context Manager that captures STDOUT into a
StringIO object

0.6
===

* added util temp_file() Context Manager that wraps the creation and removal
of temp files

0.5.1
=====

* fix py2.7 specific bug where AnchorParser wasn't initializing properly due
    to old style classes

0.5
===

* added parse_link utility for parsing HTML anchor tags

0.4
===

* added ExtendedEnum.items() method

0.3.1
=====

* restructured so tests could be called via setup.py

0.3
===

* added waelstow utilities for doing python unittests manipulation

0.2
===

* added @silence_logs

0.1.1
=====

* fixed some of the docs


0.1.0
=====

* initial pypi commit
