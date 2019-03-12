
============
Installation
============


To install the SEB Open edX plugin in an Open edX instance you need to complete 2 steps.

* Use pip to install the plugin into the same virtualenv that has all the dependencies for edxapp (edx-platform)
* Include ``seb_openedx.middleware.SecureExamBrowserMiddleware`` into the list of Middleware Classes for the django aplication.

We will go into detail on how to achieve this for the two more common ways of running Open edX.


Docker Devstack
===============

## Installation
- Clone this repo
- Execute `pip install -e .`
- Add middleware into `/edx-platform/lms/envs/common.py` as in:
    ```python
    # Use MIDDLEWARE.append instead on Django >= 2.0
    MIDDLEWARE_CLASSES.append('seb_openedx.middleware.SecureExamBrowserMiddleware')
    ```



Native Installation
===================



Other Distributions
===================

