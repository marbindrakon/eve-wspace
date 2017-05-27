# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Map', '0005_wsystem_statics'),
    ]

    operations = [
        migrations.AlterField(
            model_name='wsystem',
            name='statics',
            field=models.ManyToManyField(to='Map.WormholeType', through='Map.SystemStatic', blank=True),
        ),
    ]
