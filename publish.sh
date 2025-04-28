#!/bin/bash

# publish.sh - Publish distobject-py to PyPI or TestPyPI
# prerequisites: pip install setuptools wheel twine
# Usage: ./publish.sh [--test]

set -e

# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build new package
python setup.py sdist bdist_wheel

# Check if --test flag is passed
if [[ "$1" == "--test" ]]; then
    echo "Publishing to Test PyPI..."
    twine upload --repository-url https://test.pypi.org/legacy/ dist/*
else
    echo "Publishing to Production PyPI..."
    twine upload dist/*
fi
