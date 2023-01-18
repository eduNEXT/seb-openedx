""" Lazy load of SebCoursewareIndex to avoid errors on CMS """


from __future__ import absolute_import


class LazyImportSebCoursewareIndex:
    """ Static class LazyImportSebCoursewareIndex """
    _cached = None

    @classmethod
    def get_or_create_class(cls):
        """ import real class or use cached version of it """
        if not cls._cached:
            from seb_openedx.seb_courseware_index import SebCoursewareIndex  # pylint: disable=C0415
            cls._cached = SebCoursewareIndex
        return cls._cached
