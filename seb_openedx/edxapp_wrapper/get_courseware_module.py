""" Backend abstraction """
from importlib import import_module
from django.conf import settings


def get_courseware_module(*args, **kwargs):
    """ Creates the edxapp user """

    backend_function = settings.SEB_COURSEWARE_MODULE
    backend = import_module(backend_function)

    return backend.get_courseware_module(*args, **kwargs)
