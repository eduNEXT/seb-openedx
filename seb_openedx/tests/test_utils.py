""" Testing utils """
# pylint: disable=attribute-defined-outside-init, invalid-name
from mock import MagicMock


def get_courseware_module():
    """ helper for settings.test fake backend """

    def get_course(course_id, depth=0, **kwargs):
        """ dummy get_course function """
        return None
    fake_courseware_module = MagicMock()
    fake_courseware_module.courses.get_course = get_course
    return fake_courseware_module


def get_courseware_index_view():
    """ helper for settings.test fake backend """
    class Dummy(object):
        """ Dummy class """
        pass
    return Dummy
