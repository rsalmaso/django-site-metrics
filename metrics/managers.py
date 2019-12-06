# Copyright (C) 2016-2019, Raffaele Salmaso <raffaele@salmaso.org>
# Copyright (C) 2009-2016, Kyle Fuller and Mariusz Felisiak
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
import time

from django.db import models
from django.db.models import Q
from django.utils import timezone

from . import settings

QUERYSET_PROXY_METHODS = (
    "year",
    "month",
    "week",
    "day",
    "today",
    "this_week",
    "this_month",
    "this_year",
    "unique_visits",
    "attr_list",
    "search",
)


class RequestQuerySet(models.QuerySet):
    def year(self, year):
        return self.filter(time__year=year)

    def month(self, year=None, month=None, month_format="%b", date=None):
        if not date:
            try:
                if year and month:
                    date = timezone.make_aware(
                        datetime.datetime(*time.strptime(year + month, "%Y" + month_format)[:3])
                    )
                else:
                    raise TypeError("Request.objects.month() takes exactly 2 arguments")
            except ValueError:
                return

        # Truncate to date.
        if isinstance(date, datetime.datetime):
            date = date.date()
        # Calculate first and last day of month, for use in a date-range lookup.
        first_day = date.replace(day=1)
        if first_day.month == 12:
            last_day = first_day.replace(year=first_day.year + 1, month=1)
        else:
            last_day = first_day.replace(month=first_day.month + 1)

        lookup_kwargs = {
            "time__gte": first_day,
            "time__lt": last_day,
        }

        return self.filter(**lookup_kwargs)

    def week(self, year, week):
        try:
            date = timezone.make_aware(datetime.datetime(*time.strptime(year + "-0-" + week, "%Y-%w-%U")[:3]))
        except ValueError:
            return

        # Calculate first and last day of week, for use in a date-range lookup.
        first_day = date
        last_day = date + datetime.timedelta(days=7)
        lookup_kwargs = {
            "time__gte": first_day,
            "time__lt": last_day,
        }

        return self.filter(**lookup_kwargs)

    def day(self, year=None, month=None, day=None, month_format="%b", day_format="%d", date=None):
        if not date:
            try:
                if year and month and day:
                    date = timezone.make_aware(
                        datetime.datetime(*time.strptime(year + month + day, "%Y" + month_format + day_format)[:3])
                    )
                else:
                    raise TypeError("Request.objects.day() takes exactly 3 arguments")
            except ValueError:
                return

        return self.filter(
            time__range=(
                timezone.make_aware(datetime.datetime.combine(date, datetime.time.min)),
                timezone.make_aware(datetime.datetime.combine(date, datetime.time.max)),
            )
        )

    def today(self):
        return self.day(date=datetime.date.today())

    def this_year(self):
        return self.year(timezone.now().year)

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
    def __getattr__(self, attr, *args, **kwargs):
        if attr in QUERYSET_PROXY_METHODS:
            return getattr(self.get_query_set(), attr, None)
        super().__getattr__(*args, **kwargs)

    def active_users(self, **options):
        """
        Returns a list of active users.

        Any arguments passed to this method will be
        given to timedelta for time filtering.

        Example:
        >>> Request.object.active_users(minutes=15)
        [<User: kylef>, <User: krisje8>]
        """

        qs = self.filter(user__isnull=False)

        if options:
            time = timezone.now() - datetime.timedelta(**options)
            qs = qs.filter(time__gte=time)

        requests = qs.select_related("user").only("user")

        return set([request.user for request in requests])
