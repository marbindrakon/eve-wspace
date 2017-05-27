# -*- coding: utf-8 -*-


from django.db import migrations, models


def combine_statics(apps, schema_editor):
    """
    Custom function that combines the old static1, static2, and static3
    into a ManyToManyField called statics. Doesn't use .add() because
    django doesn't let you do that when you have an intermediate table.
    """
    WSystem = apps.get_model("Map", "WSystem")
    SystemStatic = apps.get_model("Map", "SystemStatic")
    for wsystem in WSystem.objects.all():
        # Get all the static wormholes
        hole1 = wsystem.static1
        hole2 = wsystem.static2
        # Add the wormholes to statics if the static exists
        if hole1:
            SystemStatic.objects.create(system=wsystem, static=hole1)
        if hole2:
            SystemStatic.objects.create(system=wsystem, static=hole2)


def split_statics(apps, schema_editor):
    WSystem = apps.get_model("Map", "WSystem")
    SystemStatic = apps.get_model("Map", "SystemStatic")
    for static in SystemStatic.objects.all():
        wsystem = static.system
        if not wsystem.static1:
            wsystem.static1 = static.static
        elif not wsystem.static2:
            wsystem.static2 = static.static
        else:
            print("System %s has already two statics, skipping %s." % (wsystem, static))
        wsystem.save()


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
        migrations.RunPython(combine_statics, split_statics),
        migrations.RemoveField(
            model_name='wsystem',
            name='static1',
        ),
        migrations.RemoveField(
            model_name='wsystem',
            name='static2',
        ),
    ]
