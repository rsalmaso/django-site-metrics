# Copyright (C) 2016-2020, Raffaele Salmaso <raffaele@salmaso.org>
# Copyright (C) 2009-2019, Kyle Fuller and Mariusz Felisiak
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

from .version import get_version

VERSION = (0, 1, 2, "final", 0)

__version__ = get_version(VERSION)
__copyright__ = "Copyright (C) 2009-2020 Raffaele Salmaso, Kyle Fuller, Mariusz Felisiak"
__licence__ = "BSD"
__author__ = "Raffaele Salmaso"
__email__ = "raffaele@salmaso.org"
__authors__ = [
    "Raffaele Salmaso <raffaele@salmaso.org>",
    "Kyle Fuller <kyle@fuller.li>",
    "Jannis Leidel (jezdez)",
    "krisje8 <krisje8@gmail.com>",
    "Mariusz Felisiak <felisiak.mariusz@gmail.com>",
]


default_app_config = "metrics.apps.MetricsConfig"
