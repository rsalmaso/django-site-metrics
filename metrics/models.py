# Copyright (C) 2016, Raffaele Salmaso <raffaele@salmaso.org>
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

import django
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from . import settings as request_settings
from .fields import StringField, URLField
from .managers import RequestManager
from .utils import HTTP_STATUS_CODES, browsers, engines

AUTH_USER_MODEL = getattr(settings, "AUTH_USER_MODEL", "auth.User")


class Request(models.Model):
    objects = RequestManager()

    # Response infomation
    response = models.SmallIntegerField(
        choices=HTTP_STATUS_CODES,
        default=200,
        verbose_name=_("response"),
    )

    # Request infomation
    method = StringField(
        default="GET",
        verbose_name=_("method"),
    )
    path = StringField(
        verbose_name=_("path"),
    )
    full_path = StringField(
        verbose_name=_("full path"),
    )
    query_string = JSONField(
        blank=True,
        null=True,
        verbose_name=_("query string"),
    )
    headers = JSONField(
        blank=True,
        null=True,
        verbose_name=_("headers"),
    )
    time = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        verbose_name=_("time"),
    )

    is_secure = models.BooleanField(
        default=False,
        verbose_name=_("is secure"),
    )
    is_ajax = models.BooleanField(
        default=False,
        verbose_name=_("is ajax"),
        help_text=_("Wheather this request was used via javascript."),
    )

    # User infomation
    ip = models.GenericIPAddressField(
        verbose_name=_("ip address"),
    )
    user_id = models.IntegerField(
        blank=True,
        null=True,
        verbose_name=_("user"),
    )
    referer = URLField(
        blank=True,
        null=True,
        verbose_name=_("referer"),
    )
    user_agent = StringField(
        blank=True,
        null=True,
        verbose_name=_("user agent"),
    )
    language = StringField(
        blank=True,
        null=True,
        verbose_name=_("language"),
    )

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
        # Request infomation
        self.method = request.method
        self.path = request.path
        self.full_path = request.get_full_path()
        self.headers = {k: v for k, v in request.META.items() if k.startswith("HTTP") or k.startswith("CONTENT")}
        self.query_string = request.GET
        self.is_secure = request.is_secure()
        self.is_ajax = request.is_ajax()

        # User infomation
        self.ip = request.META.get("REMOTE_ADDR", "")
        self.referer = request.META.get("HTTP_REFERER", "")
        self.user_agent = request.META.get("HTTP_USER_AGENT", "")
        self.language = request.META.get("HTTP_ACCEPT_LANGUAGE", "")

        if hasattr(request, "user") and hasattr(request.user, "is_authenticated"):
            is_authenticated = request.user.is_authenticated
            if django.VERSION < (1, 10):
                is_authenticated = is_authenticated()
            if is_authenticated:
                self.user_id = request.user.pk

        if response:
            self.response = response.status_code

            if (response.status_code == 301) or (response.status_code == 302):
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
