#!/bin/bash
#
# python pip --upgrade pip
# python pip --upgrade setuptools
# python pip --upgrade wheel

act="$1"
env="$2"

# Funcs
check_if_changelog_is_wip () {
    grep "\*\*\*WIP\*\*\*" CHANGELOG.md > /dev/null && echo "CHANGELOG.md is WIP" && exit 1
}

confirm () {
    echo -n "$1 (y/n) "
    read "ans"
    if [[ "${ans^^}" != "Y" ]]; then
        echo "$2"; exit 1
    fi
}


# Setup
if [[ "$env" == "master" ]]; then
    check_if_changelog_is_wip
fi

confirm "Have you upgraded versions?" "Please upgrade version"


# Main
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
