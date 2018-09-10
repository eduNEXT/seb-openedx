""" Backend abstraction """
from xmodule.modulestore.django import modulestore  # pylint: disable=import-error


def get_course_module(course_key, depth=0):
    """ get_course_module backend """
    return modulestore().get_course(course_key, depth=0)
