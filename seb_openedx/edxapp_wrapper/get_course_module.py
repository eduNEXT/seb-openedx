""" Backend abstraction """
from importlib import import_module
from django.conf import settings


def get_course_module(*args, **kwargs):
    """ Gets the modulestore course object """

    backend_function = settings.SEB_COURSE_MODULE
    backend = import_module(backend_function)

    return backend.get_course_module(*args, **kwargs)


def modulestore_update_item(*args, **kwargs):
    """ Update the modulestore course object """

    backend_function = settings.SEB_UPDATE_MODULESTORE
    backend = import_module(backend_function)

    return backend.modulestore_update_item(*args, **kwargs)
