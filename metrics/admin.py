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

import json
from datetime import timedelta
from functools import update_wrapper
from urllib.parse import urlencode

from django.contrib import admin
from django.contrib.admin import widgets
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.utils.text import Truncator

from .fields import StringField
from .models import Request
from .plugins import plugins
from .serializers import JSONEncoder
from .traffic import modules

User = get_user_model()


class RequestAdmin(admin.ModelAdmin):
    formfield_overrides = {
        StringField: {"widget": widgets.AdminTextInputWidget},
    }
    list_display = ("time", "_path", "response", "method", "request_from")
    fieldsets = (
        (
            _("Request"),
            {"fields": ("method", "path", "full_path", "_query_string", "time", "is_secure", "is_ajax", "_headers")},
        ),
        (_("Response"), {"fields": ("response",)}),
        (_("User info"), {"fields": ("referer", "user_agent", "ip", "_user", "language")}),
    )
    readonly_fields = (
        "method",
        "path",
        "full_path",
        "_query_string",
        "time",
        "is_secure",
        "is_ajax",
        "_headers",
        "response",
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
        return """<a href="?{url}" title="{path}">{path}</a>""".format(
            url=urlencode({"path": obj.path}), path=Truncator(obj.path).chars(72),
        )

    _path.short_description = _("Path")
    _path.allow_tags = True

    def _headers(self, obj):
        return json.dumps(obj.headers, cls=JSONEncoder, indent=2)

    def _user(self, obj):
        user = obj.get_user()
        return "{username} [{id}]".format(id=user.pk, username=user.get_username()) if user else ""

    def request_from(self, obj):
        if obj.user_id:
            user = obj.get_user()
            return format_html(
                """<a href="?user__{field}={username}" title="{title}">{user}</a>""".format(
                    field=User.USERNAME_FIELD,
                    username=Truncator(user.get_username()).chars(35),
                    title=_("Show only requests from this user."),
                    user=user,
                )
            )
        return format_html(
            """<a href="?ip={0}" title="{1}">{0}</a>""".format(obj.ip, _("Show only requests from this IP address."),)
        )

    request_from.short_description = "From"
    request_from.allow_tags = True

    def get_urls(self):
        from django.conf.urls import url

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            return update_wrapper(wrapper, view)

        info = (self.model._meta.app_label, self.model._meta.model_name)
        return [
            url(r"^overview/$", wrap(self.overview), name="{0}_{1}_overview".format(*info)),
            url(r"^overview/traffic/$", wrap(self.traffic), name="{0}_{1}_traffic".format(*info)),
        ] + super().get_urls()

    def overview(self, request):
        qs = Request.objects.this_month()
        for plugin in plugins.plugins:
            plugin.qs = qs

        return render(
            request,
            "admin/metrics/request/overview.html",
            {"title": _("Request overview"), "plugins": plugins.plugins,},
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
        days_qs = [(day, Request.objects.day(date=day)) for day in days]
        dump = json.dumps(modules.graph(days_qs), cls=JSONEncoder, indent=2)
        return HttpResponse(dump, content_type="text/javascript")


admin.site.register(Request, RequestAdmin)
