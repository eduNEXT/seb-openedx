# -*- coding: utf-8 -*-
""" Tests for public user creation API. """
from __future__ import absolute_import, unicode_literals
from django.contrib.auth import get_user_model

from django.test import TestCase
from seb_openedx.tests.test_utils import is_testing_hawthorn
import seb_openedx


class TestInfoView(TestCase):
    """ Tests for the seb-open-edx page """
    def setUp(self):
        get_user_model().objects.create_superuser('test', 'test@example.com', 'test')

    def test_version_is_present(self):
        """ Check that test version is present """
        login_success = self.client.login(username='test', password='test')
        self.assertTrue(login_success)
        url = '/seb-openedx/seb-info' if is_testing_hawthorn() else '/seb-info'
        response = self.client.get(url)
        self.assertContains(response, seb_openedx.__version__)
