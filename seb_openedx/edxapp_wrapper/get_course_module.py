""" Backend abstraction """
from importlib import import_module
from django.conf import settings


def get_course_module(*args, **kwargs):
    """ Creates the edxapp user """

    backend_function = settings.EOX_CORE_COURSE_MODULE
    backend = import_module(backend_function)

    return backend.get_course_module(*args, **kwargs)
