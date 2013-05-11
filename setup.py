#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set fileencoding=utf8 :

from setuptools import setup
import os

version = '0.0.1'

install_requires = [
    'django',
    'pymongo',
]

setup(
    name='mongine',
    version=version,
    description="Basic Django MongoDB Engine",
    # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        "Programming Language :: Python",
        ],
    keywords=['django', 'mongodb', 'mongine'],
    author='snp',
    author_email='gosu.snp@gmail.com',
    url='https://github.com/gosusnp/mongine',
    license='MIT/X',
    packages=['mongine'],
    install_requires=install_requires,
)
