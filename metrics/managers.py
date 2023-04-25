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

import datetime
import time

from dateutil.relativedelta import relativedelta
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.utils import timezone

from . import settings
from .utils import handle_naive_datetime


class RequestQuerySet(models.QuerySet):
    def year(self, year):
        return self.filter(timestamp__year=year)

    def month(self, year=None, month=None, month_format="%b", date=None):
        if not date:
            try:
                if year and month:
                    date = datetime.date(*time.strptime(year + month, "%Y" + month_format)[:3])
                else:
                    raise TypeError("Request.objects.month() takes exactly 2 arguments")
            except ValueError:
                return
        # Truncate to date.
        if isinstance(date, datetime.datetime):
            date = date.date()

        first_day = datetime.datetime.combine(date.replace(day=1), datetime.time.min)
        last_day = first_day + relativedelta(months=1)
        return self.filter(
            timestamp__gte=handle_naive_datetime(first_day),
            timestamp__lt=handle_naive_datetime(last_day),
        )

    def week(self, year, week):
        try:
            date = datetime.date(*time.strptime(year + "-0-" + week, "%Y-%w-%U")[:3])
        except ValueError:
            return

        first_day = datetime.datetime.combine(date, datetime.time.min)
        last_day = first_day + datetime.timedelta(days=7)
        return self.filter(
            timestamp__gte=handle_naive_datetime(first_day),
            timestamp__lt=handle_naive_datetime(last_day),
        )

    def day(self, year=None, month=None, day=None, month_format="%b", day_format="%d", date=None):
        if not date:
            try:
                if year and month and day:
                    date = datetime.date(*time.strptime(year + month + day, "%Y" + month_format + day_format)[:3])
                else:
                    raise TypeError("Request.objects.day() takes exactly 3 arguments")
            except ValueError:
                return
        return self.filter(
            timestamp__range=(
                handle_naive_datetime(datetime.datetime.combine(date, datetime.time.min)),
                handle_naive_datetime(datetime.datetime.combine(date, datetime.time.max)),
            )
        )

    def today(self):
        return self.day(date=datetime.date.today())

    def this_year(self):
        return self.year(datetime.date.today().year)

    def this_month(self):
        return self.month(date=datetime.date.today())

    def this_week(self):
        today = datetime.date.today()
        return self.week(str(today.year), today.strftime("%U"))

    def unique_visits(self):
        return self.exclude(referer__startswith=settings.BASE_URL)

    def attr_list(self, name):
        return [getattr(item, name, None) for item in self if hasattr(item, name)]

    def search(self):
        return self.filter(Q(referer__contains="google") | Q(referer__contains="yahoo") | Q(referer__contains="bing"))


class RequestManager(models.Manager.from_queryset(RequestQuerySet)):
    def active_users(self, **options):
        """
        Returns a list of active users.

        Any arguments passed to this method will be
        given to timedelta for time filtering.

        Example:
        >>> Request.object.active_users(minutes=15)
        [<User: kylef>, <User: krisje8>]
        """

        qs = self.exclude(user_id=None)

        if options:
            timestamp = timezone.now() - datetime.timedelta(**options)
            qs = qs.filter(timestamp__gte=timestamp)

        user_ids = qs.values_list("user_id", flat=True).order_by("user_id").distinct()

        return get_user_model().objects.filter(
            pk__in=list(user_ids),  # explicit cast to list, otherwise django will join between unrelated databases
        )
