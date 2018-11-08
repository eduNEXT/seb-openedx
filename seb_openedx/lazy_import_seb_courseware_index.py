""" Lazy load of SebCoursewareIndex to avoid errors on CMS """


class LazyImportSebCoursewareIndex(object):
    """ Static class LazyImportSebCoursewareIndex """
    _cached = None

    @classmethod
    def get_or_create_class(cls):
        """ import real class or use cached version of it """
        if not cls._cached:
            from seb_openedx.seb_courseware_index import SebCoursewareIndex
            cls._cached = SebCoursewareIndex
        return cls._cached
