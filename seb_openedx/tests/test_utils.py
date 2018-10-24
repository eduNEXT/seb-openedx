""" Testing utils """
# pylint: disable=attribute-defined-outside-init, invalid-name
from mock import MagicMock, Mock


def get_courseware_module():
    """ helper for settings.test fake backend """

    def get_course(course_id, depth=0, **kwargs):
        """ dummy get_course function """
        return None
    fake_courseware_module = MagicMock()
    fake_courseware_module.courses.get_course = get_course
    fake_courseware_module.views.index.CoursewareIndex = Mock
    return fake_courseware_module
