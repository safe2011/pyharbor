#!/usr/bin/env python
#-*- coding:utf-8 -*-

import os

from setuptools import setup, find_packages

packages = find_packages(exclude=['test', 'test.*', 'legacy_test','__pycache__'])

setup(
    name = "pyharbor",
    version = "1.0.0",
    keywords = ("pyharbor", "harbor","python"),
    description = "The harbor python SDK",
    long_description = "The harbor python SDK",
    license = "Apache License 2.0",
    url = "https://github.com/safe2011/pyharbor",
    author = "safe2011",
    author_email = "safe2011@outlook.com",
    packages = packages,
    platforms = "any",
    install_requires = [],
)

