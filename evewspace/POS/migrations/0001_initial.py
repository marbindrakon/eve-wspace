# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='POS',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('planet', models.IntegerField()),
                ('moon', models.IntegerField()),
                ('posname', models.CharField(max_length=100, null=True, blank=True)),
                ('fitting', models.TextField(null=True, blank=True)),
                ('status', models.IntegerField(choices=[(0, b'Unanchored'), (1, b'Anchored'), (2, b'Onlining'), (3, b'Reinforced'), (4, b'Online')])),
                ('rftime', models.DateTimeField(null=True, blank=True)),
                ('updated', models.DateTimeField()),
                ('guns', models.IntegerField(null=True, blank=True)),
                ('ewar', models.IntegerField(null=True, blank=True)),
                ('sma', models.IntegerField(null=True, blank=True)),
                ('hardener', models.IntegerField(null=True, blank=True)),
                ('warpin_notice', models.CharField(max_length=64, null=True, blank=True)),
            ],
            options={
                'ordering': ['system__name', 'planet', 'moon'],
            },
        ),
        migrations.CreateModel(
            name='POSApplication',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('normalfit', models.TextField()),
                ('siegefit', models.TextField()),
                ('approved', models.DateTimeField(null=True, blank=True)),
            ],
            options={
                'permissions': (('can_close_pos_app', 'Can dispose of corp POS applications.'),),
            },
        ),
        migrations.CreateModel(
            name='POSVote',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('vote', models.IntegerField(choices=[(0, b'Deny'), (1, b'Approve'), (2, b'Abstain')])),
                ('application', models.ForeignKey(related_name='votes', to='POS.POSApplication')),
            ],
        ),
        migrations.CreateModel(
            name='CorpPOS',
            fields=[
                ('pos_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='POS.POS')),
                ('password', models.CharField(max_length=100)),
                ('description', models.TextField(null=True, blank=True)),
                ('apiitemid', models.BigIntegerField(null=True, blank=True)),
            ],
            options={
                'permissions': (('can_see_pos_pw', 'Can see corp POS passwords.'), ('can_see_all_pos', 'Sees all corp POSes regardless of manager.')),
            },
            bases=('POS.pos',),
        ),
    ]
