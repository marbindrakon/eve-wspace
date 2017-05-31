# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Destination',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='Map',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100)),
                ('explicitperms', models.BooleanField(default=False)),
                ('truncate_allowed', models.BooleanField(default=True)),
            ],
            options={
                'permissions': (('map_unrestricted', 'Do not require explicit access to maps.'), ('map_admin', 'Access map configuration.')),
            },
        ),
        migrations.CreateModel(
            name='MapLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('action', models.CharField(max_length=255)),
                ('visible', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='MapPermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('access', models.IntegerField(choices=[(0, b'No Access'), (1, b'View Only'), (2, b'View / Change')])),
            ],
        ),
        migrations.CreateModel(
            name='MapSystem',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('friendlyname', models.CharField(max_length=255)),
                ('interesttime', models.DateTimeField(null=True, blank=True)),
                ('display_order_priority', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='Signature',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sigid', models.CharField(max_length=10)),
                ('updated', models.BooleanField(default=False)),
                ('info', models.CharField(max_length=65, null=True, blank=True)),
                ('activated', models.DateTimeField(null=True, blank=True)),
                ('downtimes', models.IntegerField(null=True, blank=True)),
                ('ratscleared', models.DateTimeField(null=True, blank=True)),
                ('lastescalated', models.DateTimeField(null=True, blank=True)),
                ('modified_time', models.DateTimeField(auto_now=True, null=True)),
                ('owned_time', models.DateTimeField(null=True)),
            ],
            options={
                'ordering': ['sigid'],
            },
        ),
        migrations.CreateModel(
            name='SignatureType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('shortname', models.CharField(max_length=6)),
                ('longname', models.CharField(max_length=100)),
                ('sleeprsite', models.BooleanField(default=False)),
                ('escalatable', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='SiteSpawn',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sysclass', models.IntegerField()),
                ('sitename', models.CharField(max_length=255)),
                ('spawns', models.TextField()),
            ],
        ),
        migrations.CreateModel(
            name='Snapshot',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=64)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('json', models.TextField()),
                ('description', models.CharField(max_length=255)),
            ],
        ),
    ]
