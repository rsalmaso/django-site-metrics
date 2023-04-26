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

from django.conf import settings

VALID_METHOD_NAMES = getattr(
    settings,
    "METRICS_VALID_METHOD_NAMES",
    ("get", "post", "put", "delete", "head", "options", "trace"),
)

ONLY_ERRORS = getattr(settings, "METRICS_ONLY_ERRORS", False)
IGNORE_AJAX = getattr(settings, "METRICS_IGNORE_AJAX", False)
IGNORE_IP = getattr(settings, "METRICS_IGNORE_IP", tuple())
IP_DUMMY = getattr(settings, "METRICS_IP_DUMMY", "1.1.1.1")
IGNORE_USERNAME = getattr(settings, "METRICS_IGNORE_USERNAME", tuple())
IGNORE_PATHS = getattr(settings, "METRICS_IGNORE_PATHS", tuple())
IGNORE_USER_AGENTS = getattr(settings, "METRICS_IGNORE_USER_AGENTS", tuple())

DEFAULT_REQUEST_PIPELINE = [
    "metrics.pipeline.get_logged_user",
    "metrics.pipeline.get_real_ip",
]

REQUEST_PIPELINE = getattr(settings, "METRICS_REQUEST_PIPELINE", DEFAULT_REQUEST_PIPELINE)

TRAFFIC_MODULES = getattr(
    settings,
    "METRICS_TRAFFIC_MODULES",
    (
        "metrics.traffic.UniqueVisitor",
        "metrics.traffic.UniqueVisit",
        "metrics.traffic.Hit",
    ),
)

PLUGINS = getattr(
    settings,
    "METRICS_PLUGINS",
    (
        "metrics.plugins.TrafficInformation",
        "metrics.plugins.LatestRequests",
        "metrics.plugins.TopPaths",
        "metrics.plugins.TopErrorPaths",
        "metrics.plugins.TopReferrers",
        "metrics.plugins.TopSearchPhrases",
        "metrics.plugins.TopBrowsers",
    ),
)

try:
    from django.contrib.sites.shortcuts import get_current_site
    from django.http import HttpRequest

    BASE_URL = getattr(settings, "METRICS_BASE_URL", f"http://{get_current_site(HttpRequest()).domain}")
except Exception:
    BASE_URL = getattr(settings, "METRICS_BASE_URL", "http://127.0.0.1")
