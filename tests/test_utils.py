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

import datetime

from django.test import SimpleTestCase
from django.test.utils import override_settings
from django.utils import timezone
from request.utils import handle_naive_datetime

EAT = timezone.get_fixed_timezone(180)  # Africa/Nairobi
ICT = timezone.get_fixed_timezone(420)  # Asia/Bangkok


class UtilsTests(SimpleTestCase):
    @override_settings(USE_TZ=False)
    def test_handle_naive_datetime_no_tz(self):
        naive_datetime = datetime.datetime(2017, 10, 15, 0, 0, 0, 0)
        self.assertEqual(handle_naive_datetime(naive_datetime), naive_datetime)

    @override_settings(USE_TZ=True, TIME_ZONE="Africa/Nairobi")
    def test_handle_naive_datetime_tz_aware(self):
        aware_datetime = datetime.datetime(2017, 10, 15, 0, 0, 0, 0, tzinfo=ICT)
        self.assertEqual(handle_naive_datetime(aware_datetime), aware_datetime)

    @override_settings(USE_TZ=True, TIME_ZONE="Africa/Nairobi")
    def test_handle_naive_datetime_tz_naive(self):
        naive_datetime = datetime.datetime(2017, 10, 15, 0, 0, 0, 0)
        self.assertEqual(
            handle_naive_datetime(naive_datetime),
            datetime.datetime(2017, 10, 15, 0, 0, 0, 0, tzinfo=EAT),
        )
