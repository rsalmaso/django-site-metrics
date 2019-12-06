from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('metrics', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='request',
            name='is_ajax',
        ),
    ]
