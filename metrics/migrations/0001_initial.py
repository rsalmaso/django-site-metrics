import django.contrib.postgres.fields.jsonb
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
                    django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True, verbose_name="query string"),
                ),
                (
                    "headers",
                    django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True, verbose_name="headers"),
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
