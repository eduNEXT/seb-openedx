Change Log
----------

..
   All enhancements and patches to seb_openedx will be documented
   in this file.  It adheres to the structure of https://keepachangelog.com/ ,
   but in reStructuredText instead of Markdown (for ease of incorporation into
   Sphinx documentation and the PyPI description).

   This project adheres to Semantic Versioning (https://semver.org/).

.. There should always be an "Unreleased" section for changes pending release.

Unreleased
~~~~~~~~~~

[2.0.0] - 2022-01-18
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Added
_____

* Added support from Koa to Olive.
* Added support for python 3.6 and 3.8.
* Added new backends for Nutmeg.
* Added new CI using Github Actions with python 3.6 and 3.8.

Removed
_______

* Removed support for python 2.7.
* Removed the previous CI (CircleCI).

Fixed
_____

* Fixed test dependencies for Nutmeg.
