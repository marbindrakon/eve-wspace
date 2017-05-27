# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Claim',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('shareclaimed', models.FloatField()),
                ('description', models.TextField()),
                ('bonus', models.FloatField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='ClaimPeriod',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('starttime', models.DateTimeField()),
                ('endtime', models.DateTimeField()),
                ('name', models.CharField(max_length=80)),
                ('closetime', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'permissions': (('can_close_claims', 'Close the claims period early.'), ('can_reopen_claims', 'Reopen the claims period.'), ('can_haul_loot', 'Mark the claim period as hauled.'), ('can_sell_loot', 'Mark the claim period as sold.')),
            },
        ),
        migrations.CreateModel(
            name='Fleet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('started', models.DateTimeField(auto_now_add=True)),
                ('ended', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'permissions': (('can_sitetracker', 'Use the Site Tracker system.'),),
            },
        ),
        migrations.CreateModel(
            name='PayoutEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('iskshare', models.BigIntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='PayoutReport',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('grossprofit', models.BigIntegerField()),
                ('datepaid', models.DateTimeField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='SiteRecord',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('fleetsize', models.IntegerField()),
                ('raw_points', models.IntegerField()),
                ('weighted_points', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='SiteRole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('short_name', models.CharField(unique=True, max_length=32)),
                ('long_name', models.CharField(unique=True, max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='SiteType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('shortname', models.CharField(unique=True, max_length=8)),
                ('longname', models.CharField(unique=True, max_length=80)),
                ('defunct', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='SiteWeight',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('sysclass', models.IntegerField(choices=[(1, b'C1'), (2, b'C2'), (3, b'C3'), (4, b'C4'), (5, b'C5'), (6, b'C6'), (7, b'High Sec'), (8, b'Low Sec'), (9, b'Null Sec'), (10, b'Jove'), (11, b'Jove'), (12, b'Thera'), (13, b'Small Ship')])),
                ('raw_points', models.IntegerField()),
            ],
        ),
    ]
