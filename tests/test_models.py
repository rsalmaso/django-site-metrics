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

from datetime import datetime
import socket
from unittest import mock

from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponse
from django.test import TestCase

from metrics import settings
from metrics.models import Request

User = get_user_model()


class RequestTests(TestCase):
    def test_from_http_request(self):
        http_request = HttpRequest()
        http_request.method = "PATCH"
        http_request.path = "/kylef"
        http_request.META["REMOTE_ADDR"] = "32.64.128.16"
        http_request.META["HTTP_USER_AGENT"] = "test user agent"
        http_request.META["HTTP_REFERER"] = "https://fuller.li/"

        http_response = HttpResponse(status=204)

        request = Request()
        request.from_http_request(http_request, http_response, commit=False)

        self.assertEqual(request.path, "/kylef")
        self.assertEqual(request.method, "PATCH")
        self.assertEqual(request.ip, "32.64.128.16")
        self.assertEqual(request.status_code, 204)
        self.assertEqual(request.user_agent, "test user agent")
        self.assertEqual(request.referer, "https://fuller.li/")

    def test_from_http_request_with_user(self):
        http_request = HttpRequest()
        http_request.method = "GET"
        http_request.user = User.objects.create(username="foo")

        request = Request()
        request.from_http_request(http_request, commit=False)
        self.assertEqual(request.user.id, http_request.user.id)

    def test_from_http_request_redirection(self):
        http_request = HttpRequest()
        http_request.method = "GET"
        http_response = HttpResponse(status=301)
        http_response["Location"] = "/foo"

        request = Request()
        request.from_http_request(http_request, http_response, commit=False)
        self.assertEqual(request.redirect, "/foo")

    def test_from_http_request_not_commit(self):
        http_request = HttpRequest()
        http_request.method = "GET"

        request = Request()
        request.from_http_request(http_request, commit=False)
        self.assertIsNone(request.id)

    def test_str_conversion(self):
        request = Request(method="PATCH", path="/", status_code=204)
        request.timestamp = datetime.now()
        self.assertEqual(str(request), "[{}] PATCH / 204".format(request.timestamp))

    def test_browser_detection_with_no_ua(self):
        request = Request(method="GET", path="/", status_code=200)
        self.assertEqual(request.browser, None)

    def test_browser_detection_with_no_path(self):
        request = Request(user_agent="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:43.0) Gecko/20100101 Firefox/43.0")
        self.assertEqual(request.browser, "Firefox")
        request = Request(user_agent="Mozilla/5.0 (compatible; MSIE 9.0; America Online Browser 1.1; Windows NT 5.0)")
        self.assertEqual(request.browser, "AOL")

    def test_determining_search_keywords_with_no_referer(self):
        request = Request()
        self.assertEqual(request.keywords, None)

    def test_determining_search_keywords(self):
        request = Request(
            referer="https://www.google.com/search?client=safari&rls=en&q=querykit+core+data&ie=UTF-8&oe=UTF-8"
        )
        self.assertEqual(request.keywords, "querykit core data")

    @mock.patch("metrics.models.gethostbyaddr", return_value=("foo.net", [], ["1.2.3.4"]))
    def test_hostname(self, *mocks):
        request = Request(ip="1.2.3.4")
        self.assertEqual(request.hostname, "foo.net")

    @mock.patch("metrics.models.gethostbyaddr", side_effect=socket.herror(2, "Host name lookup failure"))
    def test_hostname_invalid(self, *mocks):
        request = Request(ip="1.2.3.4")
        self.assertEqual(request.hostname, request.ip)

    def test_save(self):
        request = Request(ip="1.2.3.4")
        request.save()

    @mock.patch("metrics.models.settings.LOG_IP", False)
    def test_save_not_log_ip(self):
        request = Request(ip="1.2.3.4")
        request.save()
        self.assertEqual(settings.IP_DUMMY, request.ip)

    @mock.patch("metrics.models.settings.ANONYMOUS_IP", True)
    def test_save_anonymous_ip(self):
        request = Request(ip="1.2.3.4")
        request.save()
        self.assertTrue(request.ip.endswith(".1"))

    @mock.patch("metrics.models.settings.LOG_USER", False)
    def test_save_not_log_user(self):
        user = User.objects.create(username="foo")
        request = Request(ip="1.2.3.4", user=user)
        request.save()
        self.assertIsNone(request.user)

    def test_get_user(self):
        user = User.objects.create(username="foo")
        request = Request.objects.create(ip="1.2.3.4", user=user)
        self.assertEqual(request.user, user)
