# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0003_ssorefreshtoken'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apikey',
            name='access_mask',
            field=models.IntegerField(null=True),
        ),
    ]
