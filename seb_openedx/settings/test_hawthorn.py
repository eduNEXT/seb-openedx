"""
Settings for seb_openedx
"""
from __future__ import absolute_import, unicode_literals
try:
    from lms.envs.test import *  # pylint: disable=wildcard-import, unused-wildcard-import, import-error
    from .test import *  # pylint: disable=wildcard-import, unused-wildcard-import, import-error

    MIDDLEWARE_CLASSES = list(MIDDLEWARE_CLASSES)   # pylint: disable=used-before-assignment
    MIDDLEWARE_CLASSES.remove('openedx.core.djangoapps.safe_sessions.middleware.SafeSessionMiddleware')
except ImportError:
    pass
