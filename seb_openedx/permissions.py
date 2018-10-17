""" Permissions as classes """
import abc
import hashlib
from django.utils import six
from django.conf import settings
from seb_openedx.seb_keys_sources import get_ordered_seb_keys_sources


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
        ordered_seb_keys_sources = get_ordered_seb_keys_sources()
        header = 'HTTP_X_SAFEEXAMBROWSER_REQUESTHASH'
        for source_function in ordered_seb_keys_sources:
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


def get_enabled_permission_classes():
    """ retrieve ordered permissions from settings if available, otherwise use defaults """
    if hasattr(settings, 'SEB_PERMISSION_COMPONENTS'):
        return [globals()[comp] for comp in settings.SEB_PERMISSION_COMPONENTS]
    return [AlwaysAllowStaff, CheckSEBKeysRequestHash]
