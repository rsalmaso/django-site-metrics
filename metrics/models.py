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

from socket import gethostbyaddr

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from . import settings
from .fields import JSONField, StringField, URLField
from .managers import RequestManager
from .utils import browsers, engines, HTTP_STATUS_CODES, pipeline_import


class Request(models.Model):
    # Response information.
    status_code = models.SmallIntegerField(choices=HTTP_STATUS_CODES, default=200, verbose_name=_("status code"))

    # Response information.
    method = StringField(default="GET", verbose_name=_("method"))
    path = StringField(verbose_name=_("path"))
    full_path = StringField(verbose_name=_("full path"))
    query_params = JSONField(blank=True, default=dict, verbose_name=_("query params"))
    headers = JSONField(blank=True, default=dict, verbose_name=_("headers"))
    timestamp = models.DateTimeField(default=timezone.now, db_index=True, verbose_name=_("timestamp"))

    is_secure = models.BooleanField(default=False, verbose_name=_("is secure"))
    is_ajax = models.BooleanField(
        default=False,
        verbose_name=_("is ajax"),
        help_text=_("Whether this request was used via javascript."),
    )

    # User information.
    ip = models.GenericIPAddressField(blank=True, null=True, verbose_name=_("ip address"))
    user_id = models.IntegerField(blank=True, null=True, verbose_name=_("user"))
    referer = URLField(blank=True, verbose_name=_("referer"))
    user_agent = StringField(blank=True, verbose_name=_("user agent"))
    language = StringField(blank=True, verbose_name=_("language"))

    objects = RequestManager()

    class Meta:
        verbose_name = _("request")
        verbose_name_plural = _("requests")

    def __str__(self):
        return f"[{self.timestamp}] {self.method} {self.path} {self.status_code}"

    @property
    def user(self):
        if self.user_id:
            return get_user_model().objects.get(pk=self.user_id)
        return None

    @user.setter
    def user(self, user):
        self.user_id = user.pk

    def from_http_request(self, request, response=None, commit=True, commit_params=None):
        # implement pipeline hooks
        REQUEST_PIPELINE = [
            "metrics.pipeline.get_general_info",
            "metrics.pipeline.get_response_data",
            *settings.REQUEST_PIPELINE,
        ]
        instance = self
        for pipeline in [pipeline_import(name) for name in REQUEST_PIPELINE]:
            instance = pipeline(
                instance=instance,
                request=request,
                response=response,
                commit=commit,
                commit_params=commit_params,
            )
            if instance is None:
                break

        if commit:
            commit_params = {} if commit_params is None else commit_params
            self.save(**commit_params)

    @property
    def browser(self):
        if not self.user_agent:
            return None

        if not hasattr(self, "_browser"):
            self._browser = browsers.resolve(self.user_agent)
        return self._browser[0]

    @property
    def keywords(self):
        if not self.referer:
            return None

        if not hasattr(self, "_keywords"):
            self._keywords = engines.resolve(self.referer)
        if self._keywords:
            return " ".join(self._keywords[1]["keywords"].split("+"))
        return None

    @property
    def hostname(self):
        try:
            return gethostbyaddr(self.ip)[0]
        except Exception:  # socket.gaierror, socket.herror, etc
            return self.ip
