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

import json

from django.contrib.admin import site
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import RequestFactory, TestCase
from django.test.utils import override_settings
from django.utils.translation import _trans

from metrics.admin import RequestAdmin
from metrics.models import Request

User = get_user_model()


class LookupAllowedTest(TestCase):
    def test_lookup_allowed(self):
        admin = RequestAdmin(Request, site)
        admin.lookup_allowed("user__username", "foo")
        admin.lookup_allowed("response", 200)


class RequestFromTest(TestCase):
    def test_user_id(self):
        admin = RequestAdmin(Request, site)
        user = User.objects.create(username="foo")
        request = Request.objects.create(user=user, ip="1.2.3.4")
        admin.request_from(request)

    def test_without_user_id(self):
        admin = RequestAdmin(Request, site)
        request = Request.objects.create(ip="1.2.3.4")
        admin.request_from(request)


class GetUrlsTest(TestCase):
    def test_get_urls(self):
        admin = RequestAdmin(Request, site)
        admin.get_urls()


class OverviewTest(TestCase):
    def test_overview(self):
        admin = RequestAdmin(Request, site)
        factory = RequestFactory()
        request = factory.get("/foo")
        admin.overview(request)


class TrafficTest(TestCase):
    def setUp(self):
        self.admin = RequestAdmin(Request, site)
        self.factory = RequestFactory()

    def test_changelist(self):
        url = reverse("admin:request_request_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_traffic(self):
        request = self.factory.get("/foo")
        self.admin.traffic(request)

    @override_settings(USE_I18N=False)
    def test_traffic_without_i18n(self):
        del _trans.gettext
        request = self.factory.get("/foo")
        self.admin.traffic(request)

    def test_bad_days(self):
        request = self.factory.get("/foo", {"days": "foo"})
        self.admin.traffic(request)

    def test_days(self):
        for days, intervals in ((9, 10), (30, 16), (365, 13)):
            request = self.factory.get("/foo", {"days": days})
            data = json.loads(self.admin.traffic(request).content.decode())
            for single_data in data:
                self.assertEqual(len(single_data["data"]), intervals)


class RequestAdminViewsTest(TestCase):
    def setUp(self):
        user = User(username="foo", is_superuser=True, is_staff=True)
        user.set_password("bar")
        user.save()
        self.client.login(username=user.username, password="bar")

    def test_overview(self):
        url = reverse("admin:metrics_request_overview")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_traffic(self):
        url = reverse("admin:metrics_request_traffic")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        json_response = json.loads(response.content.decode())
        self.assertIsInstance(json_response, list)
        self.assertIsInstance(json_response[0], dict)
        self.assertIn("data", json_response[0])
        self.assertIn("label", json_response[0])
        for time, value in json_response[0]["data"]:
            self.assertIsInstance(time, float)
            self.assertIsInstance(value, int)
