""" SebCoursewareIndex """
from seb_openedx.edxapp_wrapper.get_courseware_module import get_courseware_module
COURSEWARE = get_courseware_module()


class SebCoursewareIndex(COURSEWARE.views.index.CoursewareIndex):
    """ Class to extend Open edX class CoursewareIndex and change _create_courseware_context """
    fragment = None

    @classmethod
    def set_context_fragment(cls, new_fragment):
        """ set for later usage at context["fragment"] """
        cls.fragment = new_fragment

    def _create_courseware_context(self, *args, **kwargs):
        """ ovrriding method (but still calling the overwritten one) """
        result = super(SebCoursewareIndex, self)._create_courseware_context(*args, **kwargs)
        if self.__class__.fragment:
            result['fragment'] = self.__class__.fragment
        self._context = result  # pylint: disable=attribute-defined-outside-init
        return result
