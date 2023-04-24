# Copyright (C) Raffaele Salmaso <raffaele@salmaso.org>
# Copyright (C) 2009-2023, Kyle Fuller and Mariusz Felisiak
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.

from unittest import mock

from django.contrib.auth import get_user_model
from django.http import HttpResponse, HttpResponseServerError
from django.test import RequestFactory, TestCase

from metrics.middleware import RequestMiddleware
from metrics.models import Request

User = get_user_model()


def get_response_empty(request):
    return HttpResponse()


def get_response_server_error(request):
    return HttpResponseServerError()


def set_request_meta(request, header, value):
    request.META[header] = value
    try:
        # invalidate request.headers cached_property, so can be rebuilt
        del request.headers
    except AttributeError:
        pass


def set_request_header(request, header, value):
    header = "HTTP_{}".format(header.upper().replace("-", "_"))
    set_request_meta(request, header, value)


class RequestMiddlewareTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = RequestMiddleware(get_response_empty)

    def test_record(self):
        request = self.factory.get("/foo")
        self.middleware(request)
        self.assertEqual(1, Request.objects.count())

    @mock.patch(
        "django.conf.settings.MIDDLEWARE",
        [
            "django.contrib.sessions.middleware.SessionMiddleware",
            "metrics.middleware.RequestMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
        ],
    )
    @mock.patch("django.conf.settings.MIDDLEWARE_CLASSES", None)
    def test_middleware_functions_supported(self):
        """
        Test support of a middleware factory that was introduced in Django == 1.10
        """
        request = self.factory.get("/foo")
        RequestMiddleware(request)

    @mock.patch("metrics.settings.VALID_METHOD_NAMES", ("get",))
    def test_dont_record_unvalid_method_name(self):
        request = self.factory.post("/foo")
        self.middleware(request)
        self.assertEqual(0, Request.objects.count())

    @mock.patch("metrics.middleware.settings.VALID_METHOD_NAMES", ("get",))
    def test_record_valid_method_name(self):
        request = self.factory.get("/foo")
        self.middleware(request)
        self.assertEqual(1, Request.objects.count())

    @mock.patch("metrics.middleware.settings.ONLY_ERRORS", False)
    def test_dont_record_only_error(self):
        request = self.factory.get("/foo")
        # Errored
        RequestMiddleware(get_response_server_error)(request)
        # Succeed
        self.middleware(request)
        self.assertEqual(2, Request.objects.count())

    @mock.patch("metrics.middleware.settings.ONLY_ERRORS", True)
    def test_record_only_error(self):
        request = self.factory.get("/foo")
        # Errored
        RequestMiddleware(get_response_server_error)(request)
        # Succeed
        self.middleware(request)
        self.assertEqual(1, Request.objects.count())

    @mock.patch("metrics.middleware.settings.IGNORE_PATHS", (r"^foo",))
    def test_dont_record_ignored_paths(self):
        request = self.factory.get("/foo")
        # Ignored path
        self.middleware(request)
        # Recorded
        request = self.factory.get("/bar")
        self.middleware(request)
        self.assertEqual(1, Request.objects.count())

    @mock.patch("metrics.middleware.settings.IGNORE_AJAX", True)
    def test_dont_record_ajax(self):
        request = self.factory.get("/foo")
        response = HttpResponse()
        # Non-Ajax
        self.middleware.process_response(request, response)
        # Ajax
        set_request_header(request, "x-requested-with", "XMLHttpRequest")
        self.middleware.process_response(request, response)

        self.assertEqual(1, Request.objects.count())

    @mock.patch("metrics.middleware.settings.IGNORE_AJAX", True)
    def test_dont_record_htmx(self):
        request = self.factory.get("/foo")
        # Non-htmx
        self.middleware(request)
        # htmx
        set_request_header(request, "hx-request", "true")
        self.middleware(request)
        self.assertEqual(Request.objects.count(), 1)

    @mock.patch("metrics.middleware.settings.IGNORE_AJAX", True)
    def test_record_boosted_html(self):
        self.assertEqual(Request.objects.count(), 0)
        request = self.factory.get("/foo")
        set_request_header(request, "hx-request", "true")
        set_request_header(request, "hx-boosted", "true")
        self.middleware(request)
        self.assertEqual(Request.objects.count(), 1)

    @mock.patch("metrics.middleware.settings.IGNORE_AJAX", False)
    def test_record_ajax(self):
        request = self.factory.get("/foo")
        response = HttpResponse()
        # Non-Ajax
        self.middleware.process_response(request, response)
        # Ajax
        set_request_header(request, "x-requested-with", "XMLHttpRequest")
        self.middleware.process_response(request, response)

        self.assertEqual(2, Request.objects.count())

    @mock.patch("metrics.middleware.settings.IGNORE_AJAX", False)
    def test_record_htmx(self):
        request = self.factory.get("/foo")
        # Non-htmx
        self.middleware(request)
        # htmx
        set_request_header(request, "hx-request", "true")
        self.middleware(request)
        self.assertEqual(Request.objects.count(), 2)

    @mock.patch("metrics.middleware.settings.IGNORE_IP", ("1.2.3.4",))
    def test_dont_record_ignored_ips(self):
        request = self.factory.get("/foo")
        # Ignored IP
        set_request_meta(request, "REMOTE_ADDR", "1.2.3.4")
        self.middleware(request)
        # Recorded
        set_request_meta(request, "REMOTE_ADDR", "5.6.7.8")
        self.middleware(request)
        self.assertEqual(1, Request.objects.count())

    def test_invalid_addr(self):
        request = self.factory.get("/foo")
        set_request_meta(request, "REMOTE_ADDR", "invalid-addr")
        with self.assertLogs("metrics.security.middleware", "WARNING") as cm:
            self.middleware(request)
        self.assertIn(
            "Bad request: {'ip': ['Enter a valid IPv4 or IPv6 address.']}",
            cm.output[0],
        )
        self.assertEqual(Request.objects.count(), 0)

    @mock.patch("metrics.middleware.settings.IGNORE_USER_AGENTS", (r"^.*Foo.*$",))
    def test_dont_record_ignored_user_agents(self):
        request = self.factory.get("/foo")
        # Ignored
        set_request_header(request, "user-agent", "Foo")
        self.middleware(request)
        set_request_header(request, "user-agent", "FooV2")
        self.middleware(request)
        # Recorded
        set_request_header(request, "user-agent", "Bar")
        self.middleware(request)
        set_request_header(request, "user-agent", "BarV2")
        self.middleware(request)
        self.assertEqual(2, Request.objects.count())

    @mock.patch("metrics.middleware.settings.IGNORE_USERNAME", ("foo",))
    def test_dont_record_ignored_user_names(self):
        request = self.factory.get("/foo")
        # Anonymous
        self.middleware(request)
        # Ignored
        request.user = User.objects.create(username="foo")
        self.middleware(request)
        # Recorded
        request.user = User.objects.create(username="bar")
        self.middleware(request)
        self.assertEqual(2, Request.objects.count())
