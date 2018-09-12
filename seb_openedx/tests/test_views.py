# -*- coding: utf-8 -*-
""" Tests for public user creation API. """
from __future__ import absolute_import, unicode_literals
from django.contrib.auth import get_user_model

from django.test import TestCase
import seb_openedx


class TestInfoView(TestCase):
    """ Tests for the seb-open-edx page """
    def setUp(self):
        get_user_model().objects.create_superuser('test', 'test@example.com', 'test')

    def test_version_is_present(self):
        """ Check that test version is present """
        login_success = self.client.login(username='test', password='test')
        self.assertTrue(login_success)
        response = self.client.get('/seb-info')
        self.assertContains(response, seb_openedx.__version__)
