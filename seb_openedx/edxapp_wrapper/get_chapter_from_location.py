""" Backend abstraction """
from importlib import import_module
from django.conf import settings


def get_chapter_from_location(*args, **kwargs):
    """ Creates the edxapp user """

    backend_function = settings.SEB_GET_CHAPTER_FROM_LOCATION
    backend = import_module(backend_function)

    return backend.get_chapter_from_location(*args, **kwargs)
