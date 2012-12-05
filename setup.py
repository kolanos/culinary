#!/usr/bin/env python
# Encoding: utf-8
# See: <http://docs.python.org/distutils/introduction.html>
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

VERSION = eval(filter(lambda _:_.startswith("__version__"),
    file("culinary/__init__.py").readlines())[0].split("=")[1])

setup(
    name="culinary",
    version=VERSION,
    description="A fork of Cuisine for those who like namespaces.",
    author="Michael Lavers",
    author_email="kolanos@gmail.com",
    url="http://github.com/kolanos/culinary",
    download_url="https://github.com/kolanos/culinary/tarball/v{0}".format(VERSION),
    keywords=["fabric", "chef", "ssh", "cuisine"],
    install_requires=["fabric"],
    packages=["culinary"],
    classifiers=[
        "Programming Language :: Python",
        "Development Status :: 3 - Alpha",
        "Natural Language :: English",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Utilities"
    ],
    license="BSD",
)
