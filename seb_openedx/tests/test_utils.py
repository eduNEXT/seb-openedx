""" Testing utils """
# pylint: disable=attribute-defined-outside-init, invalid-name
from mock import MagicMock
from opaque_keys.edx.django.models import CourseKey
from seb_openedx.constants import SEPARATOR_CHAR
from seb_openedx.models import SebCourseConfiguration


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
    class Dummy:
        """ Dummy class """        
    return Dummy


def get_seb_configuration_instance():
    """Get SebCourseConfiguration fake instance."""
    return SebCourseConfiguration.objects.create(
        course_id=CourseKey.from_string('course-v1:edX+DemoX+Demo_Course'),
        permission_components=SEPARATOR_CHAR.join(['AlwaysAllowStaff', 'CheckSEBHashBrowserExamKeyOrConfigKey']),
        browser_keys=SEPARATOR_CHAR.join(['browser_key1', 'browser_key2']),
        config_keys=SEPARATOR_CHAR.join(['config_key1', 'config_key2']),
        user_banning_enabled=False,
        blacklist_chapters='',
        whitelist_paths=''
    )
