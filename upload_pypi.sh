#!/bin/bash
#
# python pip --upgrade pip
# python pip --upgrade setuptools
# python pip --upgrade wheel

act="$1"
env="$2"

if [[ "$act" == "upload" ]]; then
    rm -rf dist/*
    python3 setup.py sdist bdist_wheel

    if [[ "$env" == 'test' ]]; then
        python3 -m twine upload --repository-url https://test.pypi.org/legacy/ dist/*
    elif [[ "$env" == 'master' ]]; then
        python3 -m twine upload dist/*
    fi
elif [[ "$act" == "build" ]]; then
    python3 setup.py sdist bdist_wheel
else
    echo "Usage $0 <upload|build>"
fi