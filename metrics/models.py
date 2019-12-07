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

from socket import gethostbyaddr

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from . import settings as request_settings
from .fields import JSONField, StringField, URLField
from .managers import RequestManager
from .utils import HTTP_STATUS_CODES, browsers, engines


class Request(models.Model):
    objects = RequestManager()

    # Response information.
    response = models.SmallIntegerField(choices=HTTP_STATUS_CODES, default=200, verbose_name=_("response"))

    # Response information.
    method = StringField(default="GET", verbose_name=_("method"))
    path = StringField(verbose_name=_("path"))
    full_path = StringField(verbose_name=_("full path"))
    query_string = JSONField(default=dict, verbose_name=_("query string"))
    headers = JSONField(default=dict, verbose_name=_("headers"))
    time = models.DateTimeField(default=timezone.now, db_index=True, verbose_name=_("time"))

    is_secure = models.BooleanField(default=False, verbose_name=_("is secure"))

    # User information.
    ip = models.GenericIPAddressField(verbose_name=_("ip address"))
    user_id = models.IntegerField(blank=True, null=True, verbose_name=_("user"))
    referer = URLField(blank=True, verbose_name=_("referer"))
    user_agent = StringField(blank=True, verbose_name=_("user agent"))
    language = StringField(blank=True, verbose_name=_("language"))

    class Meta:
        ordering = ["-time"]
        verbose_name = _("request")
        verbose_name_plural = _("requests")

    def __str__(self):
        return "[{0}] {1} {2} {3}".format(self.time, self.method, self.path, self.response)

    def get_user(self):
        if self.user_id:
            return get_user_model().objects.get(pk=self.user_id)
        return None

    get_user.allow_tags = True
    get_user.short_description = _("user")

    @property
    def user(self):
        return self.get_user()

    def from_http_request(self, request, response=None, commit=True):
        # Request information.
        self.method = request.method
        self.path = request.path
        self.full_path = request.get_full_path()
        self.headers = {
            k: v
            for k, v in request.META.items()
            if (k.startswith("HTTP") or k.startswith("CONTENT")) and k != "HTTP_COOKIE"
        }
        self.query_string = request.GET
        self.is_secure = request.is_secure()

        # User information.
        self.ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", "")).split(",")[0]
        self.referer = request.META.get("HTTP_REFERER", "")
        self.user_agent = request.META.get("HTTP_USER_AGENT", "")
        self.language = request.META.get("HTTP_ACCEPT_LANGUAGE", "")

        if hasattr(request, "user") and hasattr(request.user, "is_authenticated"):
            if request.user.is_authenticated:
                self.user_id = request.user.pk

        if response:
            self.response = response.status_code

            if response.status_code in [301, 302, 307, 308]:
                self.redirect = response["Location"]

        if commit:
            self.save()

    @property
    def browser(self):
        if not self.user_agent:
            return

        if not hasattr(self, "_browser"):
            self._browser = browsers.resolve(self.user_agent)
        return self._browser[0]

    @property
    def keywords(self):
        if not self.referer:
            return

        if not hasattr(self, "_keywords"):
            self._keywords = engines.resolve(self.referer)
        if self._keywords:
            return " ".join(self._keywords[1]["keywords"].split("+"))

    @property
    def hostname(self):
        try:
            return gethostbyaddr(self.ip)[0]
        except Exception:  # socket.gaierror, socket.herror, etc
            return self.ip

    def save(self, *args, **kwargs):
        if not request_settings.LOG_IP:
            self.ip = request_settings.IP_DUMMY
        elif request_settings.ANONYMOUS_IP:
            parts = self.ip.split(".")[0:-1]
            parts.append("1")
            self.ip = ".".join(parts)
        if not request_settings.LOG_USER:
            self.user_id = None

        super().save(*args, **kwargs)
