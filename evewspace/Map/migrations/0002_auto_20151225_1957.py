# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0006_require_contenttypes_0002'),
        ('Map', '0001_initial'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='System',
            fields=[
                ('systemdata_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='core.SystemData')),
                ('sysclass', models.IntegerField(choices=[(1, b'C1'), (2, b'C2'), (3, b'C3'), (4, b'C4'), (5, b'C5'), (6, b'C6'), (7, b'High Sec'), (8, b'Low Sec'), (9, b'Null Sec')])),
                ('importance', models.IntegerField(default=0, choices=[(0, b'Regular'), (1, b'Dangerous System'), (2, b'Important System')])),
                ('occupied', models.TextField(blank=True)),
                ('info', models.TextField(blank=True)),
                ('lastscanned', models.DateTimeField()),
                ('npckills', models.IntegerField(null=True, blank=True)),
                ('podkills', models.IntegerField(null=True, blank=True)),
                ('shipkills', models.IntegerField(null=True, blank=True)),
                ('updated', models.DateTimeField(null=True, blank=True)),
                ('first_visited', models.DateTimeField(null=True, blank=True)),
                ('last_visited', models.DateTimeField(null=True, blank=True)),
            ],
            bases=('core.systemdata',),
        ),
        migrations.CreateModel(
            name='Wormhole',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('top_bubbled', models.NullBooleanField()),
                ('bottom_bubbled', models.NullBooleanField()),
                ('time_status', models.IntegerField(choices=[(0, b'Fine'), (1, b'End of Life')])),
                ('mass_status', models.IntegerField(choices=[(0, b'No Shrink'), (1, b'First Shrink'), (2, b'Critical')])),
                ('updated', models.DateTimeField(auto_now=True)),
                ('eol_time', models.DateTimeField(null=True)),
                ('collapsed', models.NullBooleanField()),
                ('bottom', models.OneToOneField(related_name='parent_wormhole', null=True, to='Map.MapSystem')),
            ],
        ),
        migrations.CreateModel(
            name='WormholeType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=4)),
                ('maxmass', models.BigIntegerField()),
                ('jumpmass', models.BigIntegerField()),
                ('lifetime', models.IntegerField()),
                ('source', models.CharField(max_length=2)),
                ('destination', models.IntegerField()),
                ('target', models.CharField(max_length=15)),
            ],
        ),
        migrations.CreateModel(
            name='KSystem',
            fields=[
                ('system_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='Map.System')),
                ('sov', models.CharField(max_length=100)),
                ('jumps', models.IntegerField(null=True, blank=True)),
            ],
            bases=('Map.system',),
        ),
        migrations.CreateModel(
            name='WSystem',
            fields=[
                ('system_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='Map.System')),
                ('effect', models.CharField(max_length=50, null=True, blank=True)),
                ('is_shattered', models.NullBooleanField(default=False)),
                ('static1', models.ForeignKey(related_name='primary_statics', blank=True, to='Map.WormholeType', null=True)),
                ('static2', models.ForeignKey(related_name='secondary_statics', blank=True, to='Map.WormholeType', null=True)),
            ],
            bases=('Map.system',),
        ),
        migrations.AddField(
            model_name='wormhole',
            name='bottom_type',
            field=models.ForeignKey(related_name='+', to='Map.WormholeType'),
        ),
        migrations.AddField(
            model_name='wormhole',
            name='map',
            field=models.ForeignKey(related_name='wormholes', to='Map.Map'),
        ),
        migrations.AddField(
            model_name='wormhole',
            name='top',
            field=models.ForeignKey(related_name='child_wormholes', to='Map.MapSystem'),
        ),
        migrations.AddField(
            model_name='wormhole',
            name='top_type',
            field=models.ForeignKey(related_name='+', to='Map.WormholeType'),
        ),
        migrations.AddField(
            model_name='snapshot',
            name='user',
            field=models.ForeignKey(related_name='snapshots', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='sitespawn',
            name='sigtype',
            field=models.ForeignKey(to='Map.SignatureType'),
        ),
        migrations.AddField(
            model_name='signature',
            name='modified_by',
            field=models.ForeignKey(related_name='signatures', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='signature',
            name='owned_by',
            field=models.ForeignKey(related_name='sigs_owned', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='signature',
            name='sigtype',
            field=models.ForeignKey(related_name='sigs', blank=True, to='Map.SignatureType', null=True),
        ),
        migrations.AddField(
            model_name='signature',
            name='system',
            field=models.ForeignKey(related_name='signatures', to='Map.System'),
        ),
        migrations.AddField(
            model_name='mapsystem',
            name='map',
            field=models.ForeignKey(related_name='systems', to='Map.Map'),
        ),
        migrations.AddField(
            model_name='mapsystem',
            name='parentsystem',
            field=models.ForeignKey(related_name='childsystems', blank=True, to='Map.MapSystem', null=True),
        ),
        migrations.AddField(
            model_name='mapsystem',
            name='system',
            field=models.ForeignKey(related_name='maps', to='Map.System'),
        ),
        migrations.AddField(
            model_name='mappermission',
            name='group',
            field=models.ForeignKey(related_name='mappermissions', to='auth.Group'),
        ),
        migrations.AddField(
            model_name='mappermission',
            name='map',
            field=models.ForeignKey(related_name='grouppermissions', to='Map.Map'),
        ),
        migrations.AddField(
            model_name='maplog',
            name='map',
            field=models.ForeignKey(related_name='logentries', to='Map.Map'),
        ),
        migrations.AddField(
            model_name='maplog',
            name='user',
            field=models.ForeignKey(related_name='maplogs', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='map',
            name='root',
            field=models.ForeignKey(related_name='root', to='Map.System'),
        ),
        migrations.AddField(
            model_name='destination',
            name='user',
            field=models.ForeignKey(related_name='destinations', to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='signature',
            unique_together=set([('system', 'sigid')]),
        ),
        migrations.AddField(
            model_name='destination',
            name='system',
            field=models.ForeignKey(related_name='destinations', to='Map.KSystem'),
        ),
    ]
