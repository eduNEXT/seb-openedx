# -*- coding: utf-8 -*-
""" Permissions as classes """
import abc
import hashlib
import logging
from django.utils import six
from django.conf import settings
from seb_openedx.seb_keys_sources import get_ordered_seb_keys_sources, get_config_by_course


LOG = logging.getLogger(__name__)


@six.add_metaclass(abc.ABCMeta)
class Permission(object):
    """ Abstract class Permision """
    @abc.abstractmethod
    def check(self, request, course_key, masquerade=None):
        """ Abstract method check """
        pass


class AlwaysAllowStaff(Permission):
    """ Always allow when user.is_staff """
    def check(self, request, course_key, masquerade=None):
        """ check """
        if masquerade and masquerade.role != 'staff':
            return False
        if hasattr(request, 'user') and request.user.is_authenticated() and request.user.is_staff:
            return True
        return False


class CheckSEBHash(object):
    """ Mixin to implement the hash checking """

    def get_seb_keys(self, course_key):
        """
        Find the seb keys both in the detailed and the compact format

        compact:
            "course-v1:SEB+01+2018":[
                "cd8827e4555e4e...088a4bd5c9887f32e590"
            ]

        detailed:
            "course-v1:SEB+CK_locked+1":{
                "BROWSER_KEYS":[
                    "cd8827e4555e4e...088a4bd5c9887f32e590"
                ],
                "CONFIG_KEYS":[
                    "cd8827e4555e4e...088a4bd5c9887f32e590"
                ]
            }
        """
        for source_function in get_ordered_seb_keys_sources():
            seb_keys = source_function(course_key)
            if isinstance(seb_keys, dict):
                seb_keys = seb_keys.get(self.detailed_config_key, None)
            if seb_keys:
                return seb_keys
        return None

    def check(self, request, course_key, *args, **kwargs):
        """
        Perform the check

        1. Get the keys
        2. Concat url and key, hash them
        3. Compare value of 2) with every key
        """
        seb_keys = self.get_seb_keys(course_key)

        if seb_keys:
            header_value = request.META.get(self.http_header, None)
            for key in seb_keys:
                tohash = request.build_absolute_uri().encode() + key.encode()
                if hashlib.sha256(tohash).hexdigest() == header_value:
                    return True

            # No valid hashed key found. No access then
            return False

        # Courses not holding this keys are by default allowed to continue
        return True


class CheckSEBKeysRequestHash(CheckSEBHash, Permission):
    """ Check for SEB Browser keys, allow if there are none configured """
    http_header = 'HTTP_X_SAFEEXAMBROWSER_REQUESTHASH'
    detailed_config_key = 'BROWSER_KEYS'


class CheckSEBKeysConfigKeyHash(CheckSEBHash, Permission):
    """ Check for SEB Config keys, allow if there are none configured """
    http_header = 'HTTP_X_SAFEEXAMBROWSER_CONFIGKEYHASH'
    detailed_config_key = 'CONFIG_KEYS'


def get_enabled_permission_classes(course_key=None):
    """ retrieve ordered permissions from settings if available, otherwise use defaults """

    try:
        if course_key:
            _config = get_config_by_course(course_key)
            components = _config.get('PERMISSION_COMPONENTS', None)
            if components:
                return [globals()[comp] for comp in components]
    except Exception:
        LOG.error("Error trying to retrieve the permission classes for course %", course_key)

    if hasattr(settings, 'SEB_PERMISSION_COMPONENTS'):
        return [globals()[comp] for comp in settings.SEB_PERMISSION_COMPONENTS]

    return [AlwaysAllowStaff]
