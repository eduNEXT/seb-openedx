""" Testing utils """
# pylint: disable=attribute-defined-outside-init, invalid-name


def get_courseware_module():
    """ helper for settings.test fake backend """
    class Object(object):
        """ dummy class """
        pass

    def get_course(course_id, depth=0, **kwargs):
        """ dummy get_course function """
        return None
    fake_courseware_module = Object()
    fake_courseware_module.views = Object()
    fake_courseware_module.views.index = Object()
    fake_courseware_module.views.index.CoursewareIndex = Object
    fake_courseware_module.courses = Object()
    fake_courseware_module.courses.get_course = get_course
    return fake_courseware_module
