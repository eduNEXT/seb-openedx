""" Backend abstraction """
from __future__ import absolute_import

from importlib import import_module

from django.conf import settings


def get_configuration_helpers(*args, **kwargs):
    """ Creates the edxapp user """

    backend_function = settings.SEB_CONFIGURATION_HELPERS
    backend = import_module(backend_function)

    return backend.get_configuration_helpers(*args, **kwargs)
