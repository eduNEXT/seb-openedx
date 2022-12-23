""" Backend abstraction """
from __future__ import absolute_import

from importlib import import_module

from django.conf import settings


def get_courseware_index_view(*args, **kwargs):
    """ Gets the courseware index view (CoursewareIndex) """

    backend_function = settings.SEB_COURSEWARE_INDEX_VIEW
    backend = import_module(backend_function)

    return backend.get_courseware_index_view(*args, **kwargs)
