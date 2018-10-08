""" Backend abstraction """
from openedx.core.djangoapps.site_configuration import helpers as configuration_helpers  # pylint: disable=import-error


def get_configuration_helpers():
    """ Real backend to get configuration_helpers """
    return configuration_helpers
