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
import django.utils.timezone
import metrics.fields
import metrics.serializers
from metrics.utils import HTTP_STATUS_CODES


class Migration(migrations.Migration):

    replaces = [('metrics', '0001_initial'), ('metrics', '0002_remove_request_is_ajax'), ('metrics', '0003_update_defaults'), ('metrics', '0004_rename_time_to_timestamp'), ('metrics', '0005_rename_response_to_status_code'), ('metrics', '0006_remove_default_ordering'), ('metrics', '0007_resync'), ('metrics', '0008_switch_to_big_auto_field')]

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status_code', models.SmallIntegerField(choices=HTTP_STATUS_CODES, default=200, verbose_name='status code')),
                ('method', metrics.fields.StringField(default='GET', verbose_name='method')),
                ('path', metrics.fields.StringField(verbose_name='path')),
                ('full_path', metrics.fields.StringField(verbose_name='full path')),
                ('query_string', metrics.fields.JSONField(default=dict, encoder=metrics.serializers.JSONEncoder, verbose_name='query string')),
                ('headers', metrics.fields.JSONField(default=dict, encoder=metrics.serializers.JSONEncoder, verbose_name='headers')),
                ('timestamp', models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='timestamp')),
                ('is_secure', models.BooleanField(default=False, verbose_name='is secure')),
                ('ip', models.GenericIPAddressField(verbose_name='ip address')),
                ('user_id', models.IntegerField(blank=True, null=True, verbose_name='user')),
                ('referer', metrics.fields.URLField(blank=True, default='', verbose_name='referer')),
                ('user_agent', metrics.fields.StringField(blank=True, default='', verbose_name='user agent')),
                ('language', metrics.fields.StringField(blank=True, default='', verbose_name='language')),
            ],
            options={
                'verbose_name_plural': 'requests',
                'ordering': ['-timestamp'],
                'verbose_name': 'request',
            },
        ),
    ]
