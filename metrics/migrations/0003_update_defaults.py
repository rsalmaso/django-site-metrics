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
