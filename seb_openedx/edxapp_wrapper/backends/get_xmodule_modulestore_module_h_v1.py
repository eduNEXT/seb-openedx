""" Backend abstraction """
from xmodule import modulestore  # pylint: disable=import-error


def get_xmodule_modulestore_module():
    """ get_courseware_module backend """
    return modulestore
