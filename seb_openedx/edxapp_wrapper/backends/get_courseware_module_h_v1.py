""" Backend abstraction """
import courseware  # pylint: disable=import-error
# Avoid lazy-loading views issue
import courseware.views  # pylint: disable=import-error


def get_courseware_module():
    """ get_courseware_module backend """
    return courseware
