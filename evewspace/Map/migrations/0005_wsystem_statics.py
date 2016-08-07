# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def combine_statics(apps, schema_editor):
    """
    Custom function that combines the old static1, static2, and static3
    into a ManyToManyField called statics. Doesn't use .add() because
    django doesn't let you do that when you have an intermediate table.
    """
    WormholeType = apps.get_model("Map", "WormholeType")
    WSystem = apps.get_model("Map", "WSystem")
    SystemStatic = apps.get_model("Map", "SystemStatic")
    for wsystem in WSystem.objects.all():
        # Get all the static wormholes
        hole1 = wsystem.static1
        hole2 = wsystem.static2
        #hole3 = wsystem.static3
        # Add the wormholes to statics if the static exists
        try:
            static1 = WormholeType.objects.get(name=hole1)
            sys_static1 = SystemStatic(system=wsystem, static=static1)
            sys_static1.save()
        except WormholeType.DoesNotExist:
            pass        # Do nothing, no static to add
        try:
            static2 = WormholeType.objects.get(name=hole2)
            sys_static2 = SystemStatic(system=wsystem, static=static2)
            sys_static2.save()
        except WormholeType.DoesNotExist:
            pass        # Do nothing, no static to add


class Migration(migrations.Migration):

    dependencies = [
        ('Map', '0004_auto_20151229_1537'),
    ]

    operations = [
        migrations.CreateModel(
            name='SystemStatic',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('static', models.ForeignKey(to='Map.WormholeType', blank=True, null=True)),
                ('system', models.ForeignKey(to='Map.WSystem', blank=True, null=True)),
            ],
        ),
        migrations.AddField(
            model_name='wsystem',
            name='statics',
            field=models.ManyToManyField(to='Map.WormholeType', null=True, through='Map.SystemStatic', blank=True),
        ),
        migrations.RunPython(combine_statics),
        migrations.RemoveField(
            model_name='wsystem',
            name='static1',
        ),
        migrations.RemoveField(
            model_name='wsystem',
            name='static2',
        ),
    ]
