#!/bin/bash

git tag `grep "VERSION" version.py | cut -d "'" -f 2`

rm -rf build
rm -rf dist
python setup.py sdist
python setup.py bdist_wheel

echo "------------------------"
echo
echo "now do:"
echo "   twine upload dist/*"
echo
