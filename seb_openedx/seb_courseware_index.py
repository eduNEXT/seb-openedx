""" SebCoursewareIndex """
from __future__ import absolute_import

from seb_openedx.edxapp_wrapper.get_courseware_index_view import \
    get_courseware_index_view

CoursewareIndex = get_courseware_index_view()  # pylint: disable=invalid-name


class SebCoursewareIndex(CoursewareIndex):
    """ Class to extend Open edX class CoursewareIndex and change _create_courseware_context """
    fragment = None

    @classmethod
    def set_context_fragment(cls, new_fragment):
        """ set for later usage at context["fragment"] """
        cls.fragment = new_fragment

    def _create_courseware_context(self, *args, **kwargs):
        """ Overriding method (but still calling the overwritten one) """
        result = super(SebCoursewareIndex, self)._create_courseware_context(*args, **kwargs)
        if self.__class__.fragment:
            result['fragment'] = self.__class__.fragment
        self._context = result  # pylint: disable=attribute-defined-outside-init
        return result
