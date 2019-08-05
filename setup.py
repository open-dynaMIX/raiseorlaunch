#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
setup.py for raiseorlaunch
"""

from codecs import open
from os import path

from setuptools import setup

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="raiseorlaunch",
    version="2.3.0",
    description="A run-or-raise-application-launcher for i3 window manager.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/open-dynaMIX/raiseorlaunch",
    author="Fabio Rämi",
    license="MIT",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    keywords="i3 i3wm launcher run-or-raise navigation workspace scratchpad",
    install_requires=["i3ipc"],
    packages=["raiseorlaunch"],
    entry_points={"console_scripts": ["raiseorlaunch = raiseorlaunch.__main__:main"]},
)
