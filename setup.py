#!/usr/bin/env python
import setuptools

from pathlib import Path
from distutils.core import setup

README = Path(__file__).parent / "README.md"
with open(README, "r") as fp:
    long_description = fp.read()

setup(
    name='PyAutoBlockchain',
    version='0.5',
    description='PAB is a framework that helps with development and automation of periodic tasks on blockchains.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Manuel Pepe',
    author_email='manuelpepe-dev@outlook.com.ar',
    url = 'https://github.com/manuelpepe/PyAutoBlockchain',
    include_package_data=True,
    package_data={
        "pab": ["resources/config.schema.json"]
    },
    entry_points={
        'console_scripts': [
            'pab = pab.cli:ep',
        ],
    },
    packages=[
        'pab',
        'pab.resources',
    ],
    install_requires=[
        "web3",
        "hexbytes",
        "python-dotenv"
    ],
    extras_require={
        "ui": ["pabui"]
    }
)