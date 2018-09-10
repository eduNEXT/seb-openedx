""" Permissions as classes """
import abc
from django.utils import six


@six.add_metaclass(abc.ABCMeta)
class Permission(object):
    """ Abstract class Permision """
    @abc.abstractmethod
    def check(self, request, course_module):
        """ Abstract method check """
        pass


class AlwaysAllowStaff(Permission):
    """ Always allow when user.is_staff """
    def check(self, request, course_module):
        """ check """
        if hasattr(request, 'user') and request.user.is_authenticated() and request.user.is_staff:
            return True
        return False


class CheckSEBKeys(Permission):
    """ Check for SEB keys, allow if there are none configured """
    def check(self, request, course_module):
        """ check """
        other_settings = course_module.other_course_settings
        header = 'HTTP_X_SAFEEXAMBROWSER_CONFIGKEYHASH'
        if 'seb_keys' in other_settings and other_settings['seb_keys']:
            return bool(header in request.META and request.META[header] in other_settings['seb_keys'])
        # Courses without seb are allowed for everyone
        return True
