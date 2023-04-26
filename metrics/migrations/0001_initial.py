# Copyright (C) Raffaele Salmaso <raffaele@salmaso.org>
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

import django.utils.timezone
import metrics.fields
from django.db import migrations, models
from metrics.utils import HTTP_STATUS_CODES


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Request",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "response",
                    models.SmallIntegerField(choices=HTTP_STATUS_CODES, default=200, verbose_name="response",),
                ),
                ("method", metrics.fields.StringField(default="GET", verbose_name="method")),
                ("path", metrics.fields.StringField(verbose_name="path")),
                ("full_path", metrics.fields.StringField(verbose_name="full path")),
                (
                    "query_string",
                    models.JSONField(blank=True, null=True, verbose_name="query string"),
                ),
                (
                    "headers",
                    models.JSONField(blank=True, null=True, verbose_name="headers"),
                ),
                ("time", models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name="time")),
                ("is_secure", models.BooleanField(default=False, verbose_name="is secure")),
                (
                    "is_ajax",
                    models.BooleanField(
                        default=False,
                        help_text="Wheather this request was used via javascript.",
                        verbose_name="is ajax",
                    ),
                ),
                ("ip", models.GenericIPAddressField(verbose_name="ip address")),
                ("user_id", models.IntegerField(blank=True, null=True, verbose_name="user")),
                ("referer", metrics.fields.URLField(blank=True, null=True, verbose_name="referer")),
                ("user_agent", metrics.fields.StringField(blank=True, null=True, verbose_name="user agent")),
                ("language", metrics.fields.StringField(blank=True, null=True, verbose_name="language")),
            ],
            options={"verbose_name_plural": "requests", "ordering": ["-time"], "verbose_name": "request",},
        ),
    ]
