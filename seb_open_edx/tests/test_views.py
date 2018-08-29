# -*- coding: utf-8 -*-
""" Tests for public user creation API. """
from __future__ import absolute_import, unicode_literals

from django.test import TestCase
import seb_open_edx

JSON_CONTENT_TYPE = 'application/json'


class TestInfoView(TestCase):
    """ Tests for the seb-open-edx page """

    def test_version_is_present(self):
        """ Check that test version is present """
        response = self.client.get('/seb-open-edx')
        self.assertContains(response, seb_open_edx.__version__)
