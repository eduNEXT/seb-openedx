""" Permissions as classes """
import abc
from django.utils import six
from seb_openedx.seb_keys_sources import ORDERED_SEB_KEYS_SOURCES


@six.add_metaclass(abc.ABCMeta)
class Permission(object):
    """ Abstract class Permision """
    @abc.abstractmethod
    def check(self, request, course_key):
        """ Abstract method check """
        pass


class AlwaysAllowStaff(Permission):
    """ Always allow when user.is_staff """
    def check(self, request, course_key):
        """ check """
        if hasattr(request, 'user') and request.user.is_authenticated() and request.user.is_staff:
            return True
        return False


class CheckSEBKeys(Permission):
    """ Check for SEB keys, allow if there are none configured """
    def check(self, request, course_key):
        """ check """
        header = 'HTTP_X_SAFEEXAMBROWSER_CONFIGKEYHASH'

        for source_function in ORDERED_SEB_KEYS_SOURCES:
            seb_keys = source_function(course_key)
            if seb_keys:
                return bool(request.META.get(header, None) in seb_keys)
        # Courses without seb are allowed by default
        return True
