# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Constellation',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True, db_column=b'constellationID')),
                ('name', models.CharField(max_length=100, db_column=b'constellationName')),
                ('x', models.FloatField()),
                ('y', models.FloatField()),
                ('z', models.FloatField()),
            ],
            options={
                'db_table': 'mapConstellations',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Faction',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True, db_column=b'factionID')),
                ('name', models.CharField(max_length=300, db_column=b'factionName', blank=True)),
                ('description', models.CharField(max_length=3000, blank=True)),
                ('iconid', models.IntegerField(null=True, db_column=b'iconID', blank=True)),
            ],
            options={
                'db_table': 'chrFactions',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('itemid', models.IntegerField(serialize=False, primary_key=True, db_column=b'itemID')),
                ('name', models.CharField(max_length=100, null=True, db_column=b'itemName', blank=True)),
                ('x', models.FloatField(null=True, db_column=b'x', blank=True)),
                ('y', models.FloatField(null=True, db_column=b'y', blank=True)),
                ('z', models.FloatField(null=True, db_column=b'z', blank=True)),
                ('security', models.FloatField(null=True, db_column=b'security', blank=True)),
            ],
            options={
                'db_table': 'mapDenormalize',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='MarketGroup',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True, db_column=b'marketGroupID')),
                ('name', models.CharField(max_length=100, null=True, db_column=b'marketGroupName', blank=True)),
                ('description', models.CharField(max_length=200, null=True, blank=True)),
                ('hasTypes', models.IntegerField()),
            ],
            options={
                'db_table': 'invMarketGroups',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True, db_column=b'regionID')),
                ('name', models.CharField(max_length=100, db_column=b'regionName')),
                ('x', models.FloatField()),
                ('y', models.FloatField()),
                ('z', models.FloatField()),
            ],
            options={
                'db_table': 'mapRegions',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='StarbaseResourcePurpose',
            fields=[
                ('purpose', models.IntegerField(serialize=False, primary_key=True)),
                ('purposeText', models.CharField(max_length=100, null=True, blank=True)),
            ],
            options={
                'db_table': 'invControlTowerResourcePurposes',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SystemData',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True, db_column=b'solarSystemID')),
                ('name', models.CharField(max_length=100, db_column=b'solarSystemName')),
                ('x', models.FloatField()),
                ('y', models.FloatField()),
                ('z', models.FloatField()),
                ('security', models.FloatField()),
            ],
            options={
                'db_table': 'mapSolarSystems',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='SystemJump',
            fields=[
                ('fromregion', models.IntegerField(db_column=b'fromRegionID')),
                ('fromconstellation', models.IntegerField(db_column=b'fromConstellationID')),
                ('fromsystem', models.IntegerField(serialize=False, primary_key=True, db_column=b'fromSolarSystemID')),
                ('tosystem', models.IntegerField(primary_key=True, db_column=b'toSolarSystemID')),
                ('toconstellation', models.IntegerField(db_column=b'toConstellationID')),
                ('toregion', models.IntegerField(db_column=b'toRegionID')),
            ],
            options={
                'db_table': 'mapSolarSystemJumps',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Type',
            fields=[
                ('id', models.IntegerField(serialize=False, primary_key=True, db_column=b'typeID')),
                ('name', models.CharField(max_length=100, db_column=b'typeName')),
                ('description', models.TextField(null=True, blank=True)),
                ('volume', models.FloatField(null=True, blank=True)),
                ('published', models.BooleanField()),
            ],
            options={
                'db_table': 'invTypes',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Alliance',
            fields=[
                ('id', models.BigIntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('shortname', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='ConfigEntry',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=32)),
                ('value', models.CharField(max_length=255, null=True, blank=True)),
                ('user', models.ForeignKey(related_name='settings', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Corporation',
            fields=[
                ('id', models.BigIntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100)),
                ('ticker', models.CharField(max_length=100)),
                ('member_count', models.IntegerField()),
                ('alliance', models.ForeignKey(related_name='member_corps', blank=True, to='core.Alliance', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='NewsFeed',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255, null=True, blank=True)),
                ('description', models.CharField(max_length=255, null=True, blank=True)),
                ('url', models.CharField(max_length=255)),
                ('user', models.ForeignKey(related_name='feeds', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='LocationWormholeClass',
            fields=[
                ('location', models.ForeignKey(related_name='whclass', primary_key=True, db_column=b'locationID', serialize=False, to='core.Location')),
                ('sysclass', models.IntegerField(null=True, db_column=b'wormholeClassID', blank=True)),
            ],
            options={
                'db_table': 'mapLocationWormholeClasses',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='StarbaseResource',
            fields=[
                ('towerType', models.ForeignKey(related_name='posesfueled', primary_key=True, db_column=b'controlTowerTypeID', serialize=False, to='core.Type')),
                ('quantity', models.IntegerField(null=True, db_column=b'quantity', blank=True)),
                ('minSecurityLevel', models.FloatField(null=True, db_column=b'minSecurityLevel', blank=True)),
            ],
            options={
                'db_table': 'invControlTowerResources',
                'managed': False,
            },
        ),
        migrations.AddField(
            model_name='alliance',
            name='executor',
            field=models.ForeignKey(related_name='+', blank=True, to='core.Corporation', null=True),
        ),
        migrations.AlterUniqueTogether(
            name='configentry',
            unique_together=set([('name', 'user')]),
        ),
    ]
