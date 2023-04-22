# Copyright (C) 2009-2021, Kyle Fuller and Mariusz Felisiak
# Copyright (C) Raffaele Salmaso <raffaele@salmaso.org>
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
# THIS SOFTWARE IS PROVIDED BY KYLE FULLER ''AS IS'' AND ANY
# EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL KYLE FULLER BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from datetime import timedelta
from io import StringIO

from django.core.management.base import CommandError
from django.test import TestCase
from django.utils.timezone import now
import mock

from metrics.management.commands.purgerequests import Command as PurgeRequest
from metrics.management.commands.purgerequests import DURATION_OPTIONS
from metrics.models import Request


class PurgeRequestsTest(TestCase):
    def setUp(self):
        Request.objects.create(ip="1.2.3.4")
        request = Request.objects.create(ip="1.2.3.4")
        request.time = now() - timedelta(days=31)
        request.save()

    def test_duration_options(self, *mock):
        for opt, func in DURATION_OPTIONS.items():
            self.assertLess(func(10), now())

    @mock.patch("metrics.management.commands.purgerequests.input", return_value="yes")
    def test_purge_requests(self, *mock):
        PurgeRequest().handle(amount=1, duration="days")
        self.assertEqual(1, Request.objects.count())

    @mock.patch("metrics.management.commands.purgerequests.input", return_value="yes")
    def test_duration_without_s(self, *mock):
        PurgeRequest().handle(amount=1, duration="day")
        self.assertEqual(1, Request.objects.count())

    def test_invalid_duration(self, *mock):
        with self.assertRaises(CommandError):
            PurgeRequest().handle(amount=1, duration="foo")
        self.assertEqual(2, Request.objects.count())

    @mock.patch("sys.stdout", new_callable=StringIO)
    def test_no_request_to_delete(self, mock_stdout):
        Request.objects.all().delete()
        PurgeRequest().handle(amount=1, duration="day", interactive=False)
        self.assertIn("There are no requests to delete.", mock_stdout.getvalue())

    @mock.patch("metrics.management.commands.purgerequests.input", return_value="no")
    def test_interactive_non_confirmed(self, *mock):
        PurgeRequest().handle(amount=1, duration="days", interactive=True)
        self.assertTrue(mock[0].called)
        self.assertEqual(2, Request.objects.count())

    @mock.patch("metrics.management.commands.purgerequests.input", return_value="yes")
    def test_non_interactive(self, *mock):
        PurgeRequest().handle(amount=1, duration="days", interactive=False)
        self.assertFalse(mock[0].called)
        self.assertEqual(1, Request.objects.count())
