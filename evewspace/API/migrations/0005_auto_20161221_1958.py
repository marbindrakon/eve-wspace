# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0004_auto_20161221_1957'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apiaccessrequirement',
            name='corps_required',
            field=models.ManyToManyField(related_name='api_requirements', to='core.Corporation'),
        ),
        migrations.AlterField(
            model_name='apiaccessrequirement',
            name='groups_required',
            field=models.ManyToManyField(related_name='api_requirements', to='auth.Group'),
        ),
    ]
