#!/usr/bin/env python
import setuptools

from distutils.core import setup

setup(
    name='PyAutoBlockchain',
    version='0.1',
    description='PAB is a framework for developing and running custom tasks in crypto blockchains.',
    author='Manuel Pepe',
    author_email='manuelpepe-dev@outlook.com.ar',
    url = 'https://github.com/manuelpepe/PyAutoBlockchain',
    include_package_data=True,
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