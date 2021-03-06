#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, print_function

import os
import re

from setuptools import setup


def get_version(*file_paths):
    """Retrieves the version from the main app __init__.py"""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError('Unable to find version string.')


version = get_version("seb_openedx", "__init__.py")


setup(
    name="seb-openedx",
    version=version,
    author="eduNEXT",
    author_email="contact@edunext.co",
    url="https://github.com/eduNEXT/seb_openedx",
    description="SEB Open edX",
    long_description="",
    install_requires=[],
    scripts=[],
    license="AGPL 3.0",
    platforms=["any"],
    zip_safe=False,
    packages=[
        'seb_openedx',
    ],
    include_package_data=True,
    entry_points={
        "lms.djangoapp": [
            "seb_openedx = seb_openedx.apps:SebOpenEdxConfig",
        ],
    }
)
