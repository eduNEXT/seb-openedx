# -*- coding: utf-8 -*-
"""The generic views for the exc-core plugin project"""

from __future__ import unicode_literals

import json
from os.path import dirname, realpath
from subprocess import check_output, CalledProcessError

from django.http import HttpResponse
from django.conf import settings
from django.http import HttpResponseForbidden

import seb_openedx


def info_view(request):
    """
    Basic view to show the working version and the exact git commit of the
    installed app
    """
    if request.user.is_authenticated() and request.user.is_staff:
        try:
            working_dir = dirname(realpath(__file__))
            git_data = unicode(check_output(["git", "rev-parse", "HEAD"], cwd=working_dir))
        except CalledProcessError:
            git_data = ''

        middlewares = settings.MIDDLEWARE_CLASSES if hasattr(settings, 'MIDDLEWARE_CLASSES') else settings.MIDDLEWARE
        is_middleware_installed = 'seb_openedx.middleware.SecureExamBrowserMiddleware' in middlewares

        response_data = {
            "version": seb_openedx.__version__,
            "name": "seb_openedx",
            "git": git_data.rstrip('\r\n'),
            "middleware_installed": is_middleware_installed
        }
        return HttpResponse(
            json.dumps(response_data),
            content_type="application/json"
        )
    return HttpResponseForbidden()
