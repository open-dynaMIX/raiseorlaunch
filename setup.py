#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
setup.py for raiseorlaunch
"""

from setuptools import setup
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='raiseorlaunch',
    version='2.0.0',
    description='A run-or-raise-application-launcher for i3 window manager.',
    long_description=long_description,
    url='https://github.com/open-dynaMIX/raiseorlaunch',
    author='Fabio Rämi',
    author_email='fabio@dynamix-tontechnik.ch',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    keywords='i3 i3wm launcher run-or-raise navigation workspace scratchpad',
    install_requires=['i3ipc'],
    packages=['raiseorlaunch'],
    entry_points={
        'console_scripts': [
            'raiseorlaunch = raiseorlaunch.__main__:main',
        ],
    },
)
