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

from django.db import migrations, models
import metrics.fields
import metrics.serializers


class Migration(migrations.Migration):

    dependencies = [
        ("metrics", "0002_remove_request_is_ajax"),
    ]

    operations = [
        migrations.AlterField(
            model_name="request",
            name="headers",
            field=metrics.fields.JSONField(
                default=dict, encoder=metrics.serializers.JSONEncoder, verbose_name="headers"
            ),
        ),
        migrations.AlterField(
            model_name="request",
            name="language",
            field=metrics.fields.StringField(blank=True, default="", verbose_name="language"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="request",
            name="query_string",
            field=metrics.fields.JSONField(
                default=dict, encoder=metrics.serializers.JSONEncoder, verbose_name="query string"
            ),
        ),
        migrations.AlterField(
            model_name="request",
            name="referer",
            field=metrics.fields.URLField(blank=True, default="", verbose_name="referer"),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="request",
            name="user_agent",
            field=metrics.fields.StringField(blank=True, default="", verbose_name="user agent"),
            preserve_default=False,
        ),
    ]
