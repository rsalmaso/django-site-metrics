import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.utils.timezone
import metrics.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Request',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('response', models.SmallIntegerField(choices=[(100, 'Continue'), (101, 'Switching Protocols'), (102, 'Processing (WebDAV)'), (200, 'OK'), (201, 'Created'), (202, 'Accepted'), (203, 'Non-Authoritative Information'), (204, 'No Content'), (205, 'Reset Content'), (206, 'Partial Content'), (207, 'Multi-Status (WebDAV)'), (300, 'Multiple Choices'), (301, 'Moved Permanently'), (302, 'Found'), (303, 'See Other'), (304, 'Not Modified'), (305, 'Use Proxy'), (306, 'Switch Proxy'), (307, 'Temporary Redirect'), (400, 'Bad Request'), (401, 'Unauthorized'), (402, 'Payment Required'), (403, 'Forbidden'), (404, 'Not Found'), (405, 'Method Not Allowed'), (406, 'Not Acceptable'), (407, 'Proxy Authentication Required'), (408, 'Request Timeout'), (409, 'Conflict'), (410, 'Gone'), (411, 'Length Required'), (412, 'Precondition Failed'), (413, 'Request Entity Too Large'), (414, 'Request-URI Too Long'), (415, 'Unsupported Media Type'), (416, 'Requested Range Not Satisfiable'), (417, 'Expectation Failed'), (418, 'I"m a teapot'), (422, 'Unprocessable Entity (WebDAV)'), (423, 'Locked (WebDAV)'), (424, 'Failed Dependency (WebDAV)'), (425, 'Unordered Collection'), (426, 'Upgrade Required'), (449, 'Retry With'), (500, 'Internal Server Error'), (501, 'Not Implemented'), (502, 'Bad Gateway'), (503, 'Service Unavailable'), (504, 'Gateway Timeout'), (505, 'HTTP Version Not Supported'), (506, 'Variant Also Negotiates'), (507, 'Insufficient Storage (WebDAV)'), (509, 'Bandwidth Limit Exceeded'), (510, 'Not Extended')], default=200, verbose_name='response')),
                ('method', metrics.fields.StringField(default='GET', verbose_name='method')),
                ('path', metrics.fields.StringField(verbose_name='path')),
                ('full_path', metrics.fields.StringField(verbose_name='full path')),
                ('query_string', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True, verbose_name='query string')),
                ('headers', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True, verbose_name='headers')),
                ('time', models.DateTimeField(db_index=True, default=django.utils.timezone.now, verbose_name='time')),
                ('is_secure', models.BooleanField(default=False, verbose_name='is secure')),
                ('is_ajax', models.BooleanField(default=False, help_text='Wheather this request was used via javascript.', verbose_name='is ajax')),
                ('ip', models.GenericIPAddressField(verbose_name='ip address')),
                ('user_id', models.IntegerField(blank=True, null=True, verbose_name='user')),
                ('referer', metrics.fields.URLField(blank=True, null=True, verbose_name='referer')),
                ('user_agent', metrics.fields.StringField(blank=True, null=True, verbose_name='user agent')),
                ('language', metrics.fields.StringField(blank=True, null=True, verbose_name='language')),
            ],
            options={
                'verbose_name_plural': 'requests',
                'ordering': ['-time'],
                'verbose_name': 'request',
            },
        ),
    ]
