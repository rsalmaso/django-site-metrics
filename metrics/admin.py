# Copyright (C) 2016-2021, Raffaele Salmaso <raffaele@salmaso.org>
# Copyright (C) 2009-2021, Kyle Fuller and Mariusz Felisiak
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
from functools import update_wrapper
import json
from urllib.parse import urlencode

from django.contrib import admin
from django.contrib.admin import widgets
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import path
from django.utils import timezone
from django.utils.html import format_html
from django.utils.text import Truncator
from django.utils.translation import gettext_lazy as _

from .fields import StringField
from .models import Request
from .plugins import plugins
from .serializers import JSONEncoder
from .traffic import modules

User = get_user_model()


@admin.register(Request)
class RequestAdmin(admin.ModelAdmin):
    formfield_overrides = {
        StringField: {"widget": widgets.AdminTextInputWidget},
    }
    list_display = ("timestamp", "_path", "status_code", "method", "request_from")
    fieldsets = (
        (
            _("Request"),
            {"fields": ("method", "path", "full_path", "_query_string", "timestamp", "is_secure", "_headers")},
        ),
        (_("Response"), {"fields": ("status_code",)}),
        (_("User info"), {"fields": ("referer", "user_agent", "ip", "_user", "language")}),
    )
    ordering = ["-timestamp"]
    readonly_fields = (
        "method",
        "path",
        "full_path",
        "_query_string",
        "timestamp",
        "is_secure",
        "_headers",
        "status_code",
        "referer",
        "user_agent",
        "ip",
        "_user",
        "language",
    )

    def lookup_allowed(self, key, value):
        return key == "user__%s" % User.USERNAME_FIELD or super().lookup_allowed(key, value)

    def _query_string(self, obj):
        return json.dumps(obj.query_string, cls=JSONEncoder, indent=2)

    def _path(self, obj):
        url = urlencode({"path": obj.path})
        path = Truncator(obj.path).chars(72)
        return format_html(f"""<a href="?{url}" title="{path}">{path}</a>""")

    _path.short_description = _("Path")

    def _headers(self, obj):
        return json.dumps(obj.headers, cls=JSONEncoder, indent=2)

    def _user(self, obj):
        user = obj.user
        return f"{user.get_username()} [{user.pk}]" if user else ""

    def request_from(self, obj):
        if obj.user_id:
            user = obj.user
            field = User.USERNAME_FIELD
            username = Truncator(user.get_username()).chars(35)
            title = _("Show only requests from this user.")
            return format_html(f"""<a href="?user__{field}={username}" title="{title}">{user}</a>""")
        ip = obj.ip
        title = _("Show only requests from this IP address.")
        return format_html(f"""<a href="?ip={ip}" title="{title}">{ip}</a>""")

    request_from.short_description = "From"

    def get_urls(self):
        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            return update_wrapper(wrapper, view)

        info = (self.model._meta.app_label, self.model._meta.model_name)
        return [
            path("overview/", wrap(self.overview), name="{0}_{1}_overview".format(*info)),
            path("overview/traffic/", wrap(self.traffic), name="{0}_{1}_traffic".format(*info)),
        ] + super().get_urls()

    def overview(self, request):
        qs = Request.objects.this_month().order_by("timestamp")
        for plugin in plugins.plugins:
            plugin.qs = qs

        return render(
            request,
            "admin/metrics/request/overview.html",
            {"title": _("Request overview"), "plugins": plugins.plugins},
        )

    def traffic(self, request):
        try:
            days_count = int(request.GET.get("days", 30))
        except ValueError:
            days_count = 30

        if days_count < 10:
            days_step = 1
        elif days_count < 60:
            days_step = 2
        else:
            days_step = 30

        days = [timezone.now().today() - timedelta(day) for day in range(0, days_count + 1, days_step)]
        days_qs = [(day, Request.objects.day(date=day).order_by("timestamp")) for day in days]
        dump = json.dumps(modules.graph(days_qs), cls=JSONEncoder, indent=2)
        return HttpResponse(dump, content_type="text/javascript")
