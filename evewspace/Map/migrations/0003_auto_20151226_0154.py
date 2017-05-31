# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Map', '0002_auto_20151225_1957'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maplog',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True, db_index=True),
        ),
    ]
