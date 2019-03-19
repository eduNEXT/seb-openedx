# -*- coding: utf-8 -*-
""" Tests for the classes that check the SEB Http hashes. """
import hashlib
import mock
from mock import Mock, patch
from django.test import RequestFactory, TestCase
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test.utils import override_settings
from seb_openedx.permissions import (
    AlwaysAllowStaff,
    CheckSEBKeysRequestHash,
    CheckSEBKeysConfigKeyHash,
)

class TestPermissionClasses(TestCase):
    """ Unitary tests for the permission classes """

    def test_allow_staff_check(self):
        """ Users with the is_staff property are allowed """
        request = Mock()
        request.user.is_staff = True

        self.assertTrue(AlwaysAllowStaff().check(request, "fake_course_id"))

        request.user.is_staff = False
        self.assertFalse(AlwaysAllowStaff().check(request, "fake_course_id"))

    @override_settings(SEB_KEY_SOURCES=['from_global_settings'], SEB_KEYS={"fake_course_id": ["fake_seb_key"]})
    def test_browser_keys_permission_no_key(self):
        request = Mock()
        request.META = {"HTTP_X_SAFEEXAMBROWSER_REQUESTHASH": None}
        request.build_absolute_uri.return_value = "https://domain.com/path"

        self.assertFalse(CheckSEBKeysRequestHash().check(request, "fake_course_id"))

    @override_settings(SEB_KEY_SOURCES=['from_global_settings'], SEB_KEYS={"fake_course_id": ["534b5a6a593e735e9d"]})
    def test_browser_keys_permission_valid_key(self):
        request = Mock()
        request.build_absolute_uri.return_value = "https://domain.com/path"
        request.META = {"HTTP_X_SAFEEXAMBROWSER_REQUESTHASH": "a3a793a2715bdd3da1a7ef3ebe8acdd48c1468433d88cba346a437e961f601b1"}  # Manually calculated

        self.assertTrue(CheckSEBKeysRequestHash().check(request, "fake_course_id"))

    @override_settings(SEB_KEY_SOURCES=['from_global_settings'], SEB_KEYS={"fake_course_id": ["534b5a6a593e735e9d"]})
    def test_config_keys_permission(self):
        pass
