""" Backend abstraction """
# Avoid lazy-loading views issue
from lms.djangoapps.courseware.views.index import CoursewareIndex  # pylint: disable=import-error


def get_courseware_index_view():
    """ get_courseware_module backend """
    return CoursewareIndex
