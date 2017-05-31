# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0005_auto_20161221_1958'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ssorefreshtoken',
            name='access_token',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='ssorefreshtoken',
            name='refresh_token',
            field=models.CharField(max_length=255, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='ssorefreshtoken',
            name='valid_until',
            field=models.DateTimeField(null=True, blank=True),
        ),
    ]
