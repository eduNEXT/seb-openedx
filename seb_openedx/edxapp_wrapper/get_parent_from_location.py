""" Backend abstraction """
from __future__ import absolute_import

from importlib import import_module

from django.conf import settings


def get_parent_from_location(*args, **kwargs):
    """ Finds the ID of a parent block from the tree """

    backend_function = settings.SEB_GET_CHAPTER_FROM_LOCATION
    backend = import_module(backend_function)
    levels = {
        'chapter': 1,
        'sequence': 2,
        'vertical': 3,
    }
    try:
        return backend.get_chapter_from_location(depth=levels.get(kwargs.pop('level')), *args, **kwargs)
    except Exception:  # pylint: disable=broad-except
        return None
