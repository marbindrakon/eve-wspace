# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Map', '0003_auto_20151226_0154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='system',
            name='sysclass',
            field=models.IntegerField(choices=[(1, b'C1'), (2, b'C2'), (3, b'C3'), (4, b'C4'), (5, b'C5'), (6, b'C6'), (7, b'High Sec'), (8, b'Low Sec'), (9, b'Null Sec'), (99, b'Unknown')]),
        ),
    ]
