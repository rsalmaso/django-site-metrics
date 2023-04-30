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

import logging

from django.core.exceptions import ValidationError

from metrics import get_request_model

from . import settings
from .router import Patterns
from .utils import request_is_ajax

logger = logging.getLogger("metrics.security.middleware")
Request = get_request_model()


class RequestMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.method.lower() not in settings.VALID_METHOD_NAMES:
            return response

        if response.status_code < 400 and settings.ONLY_ERRORS:
            return response

        ignore = Patterns(False, *settings.IGNORE_PATHS)
        if ignore.resolve(request.path[1:]):
            return response

        if request_is_ajax(request) and settings.IGNORE_AJAX:
            return response

        if request.META.get("REMOTE_ADDR") in settings.IGNORE_IP:
            return response

        ignore = Patterns(False, *settings.IGNORE_USER_AGENTS)
        if ignore.resolve(request.headers.get("user-agent", "")):
            return response

        if getattr(request, "user", False):
            if hasattr(request.user, "get_username") and request.user.get_username() in settings.IGNORE_USERNAME:
                return response

        instance = Request()
        try:
            instance.from_http_request(request, response, commit=False)
            instance.full_clean()
        except ValidationError as exc:
            logger.warning(
                "Bad request: %s",
                str(exc),
                exc_info=exc,
                extra={"status_code": 400, "request": request},
            )
        else:
            instance.save()
        return response
