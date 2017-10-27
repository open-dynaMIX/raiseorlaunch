#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
setup.py for raiseorlaunch
"""

from setuptools import setup
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='raiseorlaunch',
    version='0.1.0',
    description='Run-or-raise-application-launcher for i3 window manager.',
    long_description=long_description,
    url='https://github.com/open-dynaMIX/raiseorlaunch',
    author='Fabio Rämi',
    author_email='fabio@dynamix-tontechnik.ch',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: POSIX :: Linux',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
    ],
    keywords='i3 run-or-raise launcher navigation',
    install_requires=['i3-py'],
    py_modules=['raiseorlaunch'],
    entry_points={
        'console_scripts': [
            'raiseorlaunch=raiseorlaunch:main',
        ],
    },
)
