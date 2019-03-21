# -*- coding: utf-8 -*-
""" Tests for the classes that check the SEB Http hashes. """
from mock import Mock
from django.test import TestCase
from django.test.utils import override_settings
from seb_openedx.permissions import (
    AlwaysAllowStaff,
    CheckSEBHashBrowserExamKey,
    CheckSEBHashConfigKey,
    CheckSEBHashBrowserExamKeyOrConfigKey,
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

    @override_settings(SEB_KEY_SOURCES=['from_global_settings'], SAFE_EXAM_BROWSER={"fake_course_id": ["fake_browser_key"]})
    def test_browser_keys_no_key(self):
        """ Having no key hash results in access denied """
        request = Mock()
        request.META = {"HTTP_X_SAFEEXAMBROWSER_REQUESTHASH": None}
        request.build_absolute_uri.return_value = "https://domain.com/path"

        self.assertFalse(CheckSEBHashBrowserExamKey().check(request, "fake_course_id"))

    @override_settings(SEB_KEY_SOURCES=['from_global_settings'], SAFE_EXAM_BROWSER={"fake_course_id": ["534b5a6a593e735e9d"]})
    def test_browser_keys_valid_key(self):
        """ Having a valid hash results in access granted """
        request = Mock()
        request.build_absolute_uri.return_value = "https://domain.com/path"
        request.META = {
            "HTTP_X_SAFEEXAMBROWSER_REQUESTHASH": "a3a793a2715bdd3da1a7ef3ebe8acdd48c1468433d88cba346a437e961f601b1"
        }

        self.assertTrue(CheckSEBHashBrowserExamKey().check(request, "fake_course_id"))

    @override_settings(SEB_KEY_SOURCES=['from_global_settings'], SAFE_EXAM_BROWSER={"fake_course_id": ["534b5a6a593e735e9d"]})
    def test_browser_keys_invalid_key(self):
        """ Having an invalid hash results in access denied """
        request = Mock()
        request.build_absolute_uri.return_value = "https://domain.com/path"
        request.META = {"HTTP_X_SAFEEXAMBROWSER_REQUESTHASH": "invalid"}

        self.assertFalse(CheckSEBHashBrowserExamKey().check(request, "fake_course_id"))

    @override_settings(SEB_KEY_SOURCES=['from_global_settings'], SAFE_EXAM_BROWSER={"fake_course_id": ["fake_config_key"]})
    def test_config_keys_no_key(self):
        """ Having no key hash results in access denied """
        request = Mock()
        request.META = {"HTTP_X_SAFEEXAMBROWSER_CONFIGKEYHASH": None}
        request.build_absolute_uri.return_value = "https://domain.com/path"

        self.assertFalse(CheckSEBHashConfigKey().check(request, "fake_course_id"))

    @override_settings(SEB_KEY_SOURCES=['from_global_settings'], SAFE_EXAM_BROWSER={"fake_course_id": ["534b5a6a593e735e9d"]})
    def test_config_keys_valid_key(self):
        """ Having a valid hash results in access granted """
        request = Mock()
        request.META = {
            "HTTP_X_SAFEEXAMBROWSER_CONFIGKEYHASH": "a3a793a2715bdd3da1a7ef3ebe8acdd48c1468433d88cba346a437e961f601b1"
        }
        request.build_absolute_uri.return_value = "https://domain.com/path"

        self.assertTrue(CheckSEBHashConfigKey().check(request, "fake_course_id"))

    @override_settings(SEB_KEY_SOURCES=['from_global_settings'], SAFE_EXAM_BROWSER={"fake_course_id": ["534b5a6a593e735e9d"]})
    def test_config_keys_invalid_key(self):
        """ Having an invalid hash results in access denied """
        request = Mock()
        request.build_absolute_uri.return_value = "https://domain.com/path"
        request.META = {"HTTP_X_SAFEEXAMBROWSER_CONFIGKEYHASH": "invalid"}

        self.assertFalse(CheckSEBHashConfigKey().check(request, "fake_course_id"))

    @override_settings(SEB_KEY_SOURCES=['from_global_settings'], SAFE_EXAM_BROWSER={"fake_course_id": ["534b5a6a593e735e9d"]})
    def test_either_key_both_invalid(self):
        """ Having both invalid hashes results in access denied """
        request = Mock()
        request.build_absolute_uri.return_value = "https://domain.com/path"
        request.META = {
            "HTTP_X_SAFEEXAMBROWSER_REQUESTHASH": "invalid",
            "HTTP_X_SAFEEXAMBROWSER_CONFIGKEYHASH": "invalid",
        }

        self.assertFalse(CheckSEBHashBrowserExamKeyOrConfigKey().check(request, "fake_course_id"))

    @override_settings(SEB_KEY_SOURCES=['from_global_settings'], SAFE_EXAM_BROWSER={"fake_course_id": ["534b5a6a593e735e9d"]})
    def test_either_key_bek_valid(self):
        """ Having a valid Browser key results in access granted """
        request = Mock()
        request.build_absolute_uri.return_value = "https://domain.com/path"
        request.META = {
            "HTTP_X_SAFEEXAMBROWSER_REQUESTHASH": "a3a793a2715bdd3da1a7ef3ebe8acdd48c1468433d88cba346a437e961f601b1",
            "HTTP_X_SAFEEXAMBROWSER_CONFIGKEYHASH": "invalid",
        }

        self.assertTrue(CheckSEBHashBrowserExamKeyOrConfigKey().check(request, "fake_course_id"))

    @override_settings(SEB_KEY_SOURCES=['from_global_settings'], SAFE_EXAM_BROWSER={"fake_course_id": ["534b5a6a593e735e9d"]})
    def test_either_key_ck_valid(self):
        """ Having a valid Config key results in access granted """
        request = Mock()
        request.build_absolute_uri.return_value = "https://domain.com/path"
        request.META = {
            "HTTP_X_SAFEEXAMBROWSER_REQUESTHASH": "invalid",
            "HTTP_X_SAFEEXAMBROWSER_CONFIGKEYHASH": "a3a793a2715bdd3da1a7ef3ebe8acdd48c1468433d88cba346a437e961f601b1",
        }

        self.assertTrue(CheckSEBHashBrowserExamKeyOrConfigKey().check(request, "fake_course_id"))

    @override_settings(SEB_KEY_SOURCES=['from_global_settings'], SAFE_EXAM_BROWSER={"fake_course_id": ["534b5a6a593e735e9d"]})
    def test_either_key_both_valid(self):
        """ Having a valid Config key and valid Browser key results in access granted """
        request = Mock()
        request.build_absolute_uri.return_value = "https://domain.com/path"
        request.META = {
            "HTTP_X_SAFEEXAMBROWSER_REQUESTHASH": "a3a793a2715bdd3da1a7ef3ebe8acdd48c1468433d88cba346a437e961f601b1",
            "HTTP_X_SAFEEXAMBROWSER_CONFIGKEYHASH": "a3a793a2715bdd3da1a7ef3ebe8acdd48c1468433d88cba346a437e961f601b1",
        }

        self.assertTrue(CheckSEBHashBrowserExamKeyOrConfigKey().check(request, "fake_course_id"))
