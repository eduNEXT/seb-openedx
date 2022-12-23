""" Backend abstraction """
from lms.djangoapps import courseware # pylint: disable=import-error


def get_courseware_module():
    """ get_courseware_module backend """
    return courseware
