""" Backend abstraction """
from importlib import import_module
from django.conf import settings


def get_edxmako_module(*args, **kwargs):
    """ Creates the edxapp user """

    backend_function = settings.SEB_EDXMAKO_MODULE
    backend = import_module(backend_function)

    return backend.get_edxmako_module(*args, **kwargs)
