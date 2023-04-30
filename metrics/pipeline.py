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

from . import settings
from .utils import request_is_ajax


def get_general_info(instance, request, response, **kwargs):
    """Gather all anonymous info from request"""
    instance.method = request.method
    instance.path = request.path
    instance.full_path = request.get_full_path()
    instance.query_params = dict(request.GET)
    instance.headers = dict(request.headers)
    try:
        del instance.headers["Cookie"]
    except KeyError:
        pass
    instance.referer = request.headers.get("referer", "")
    instance.user_agent = request.headers.get("user-agent", "")
    instance.language = request.headers.get("accept-language", "")
    instance.is_secure = request.is_secure()
    instance.is_ajax = request_is_ajax(request)

    return instance


def get_response_data(instance, request, response, **kwargs):
    """Get response info"""
    if response:
        instance.status_code = response.status_code
        if response.status_code in [301, 302, 307, 308]:
            instance.redirect = response["Location"]

    return instance


def get_real_ip(instance, request, **kwargs):
    """Try to retrieve the real ip.
    https://www.brainonfire.net/blog/2022/03/04/understanding-using-xff/
    """
    instance.ip = request.headers.get("x-forwarded-for", request.META.get("REMOTE_ADDR", "")).split(",")[0]

    return instance


def get_dummy_ip(instance, **kwargs):
    """Always set a dummy IP (same as the default value)"""
    instance.ip = settings.IP_DUMMY

    return instance


def get_anonymized_ip(instance, **kwargs):
    """Anonymize current ip (or set as dummy)"""
    if instance.ip:
        parts = instance.ip.split(".")[0:-1]
        parts.append("1")
        instance.ip = ".".join(parts)
    else:
        instance.ip = settings.IP_DUMMY

    return instance


def get_logged_user(instance, request, **kwargs):
    """Retrieve current logged user."""
    if hasattr(request, "user") and hasattr(request.user, "is_authenticated"):
        if request.user.is_authenticated:
            instance.user_id = request.user.pk

    return instance


def unset_user(instance, **kwargs):
    """Always unset retrieve user"""
    instance.user_id = None

    return instance


def unset_ip(instance, **kwargs):
    """Always unset logged IP"""
    instance.ip = None

    return instance
