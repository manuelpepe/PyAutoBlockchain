#!/usr/bin/env python
import setuptools

from distutils.core import setup

setup(
    name='PyAutoBlockchain',
    version='1.0',
    description='PAB is a framework for developing and running custom tasks in crypto blockchains.',
    author='Manuel Pepe',
    author_email='manuelpepe-dev@outlook.com.ar',
    url = 'https://github.com/manuelpepe/PyAutoBlockchain',
    entry_points={
        'console_scripts': [
            'pab = pab.cli:main',
        ],
    },
    packages=[
        'pab',
        'pab.resources',
    ],
    install_requires=[
        "web3",
        "hexbytes"
    ]
)