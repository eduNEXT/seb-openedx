""" Permissions as classes """
import abc
import hashlib
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


class CheckSEBKeysRequestHash(Permission):
    """ Check for SEB keys, allow if there are none configured """
    def check(self, request, course_key):
        """ check """

        header = 'HTTP_X_SAFEEXAMBROWSER_REQUESTHASH'
        for source_function in ORDERED_SEB_KEYS_SOURCES:
            seb_keys = source_function(course_key)
            if seb_keys:
                header_value = request.META.get(header, None)
                for key in seb_keys:
                    tohash = request.build_absolute_uri().encode() + key.encode()
                    if hashlib.sha256(tohash).hexdigest() == header_value:
                        return True
                # No valid hashed key found, abort
                return False
        # Courses without seb are allowed by default
        return True


class CheckSEBKeysConfigKeyHash(Permission):
    """ Check for SEB keys, allow if there are none configured """
    def check(self, request, course_key):
        """ check """
        # header = 'HTTP_X_SAFEEXAMBROWSER_CONFIGKEY HASH'
        # TODO: Pending implementation!
        return False
