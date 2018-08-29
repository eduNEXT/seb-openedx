#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version(*file_paths):
    """Retrieves the version from the main app __init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


version = get_version("seb_open_edx", "__init__.py")


setup(
    name="seb_open_edx",
    version=version,
    author="eduNEXT",
    author_email="contact@edunext.co",
    url="https://github.com/eduNEXT/seb_open_edx",
    description="eduNEXT Openedx extensions",
    long_description="",
    install_requires=[],
    scripts=[],
    license="AGPL",
    platforms=["any"],
    zip_safe=False,
    packages=['seb_open_edx'],
    include_package_data=True,
    entry_points={
        "lms.djangoapp": [
            "seb_open_edx = seb_open_edx.apps:SebOpenEdxConfig",
        ],
    }
)
