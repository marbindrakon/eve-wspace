# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0006_require_contenttypes_0002'),
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='SubscriptionGroup',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=64)),
                ('desc', models.CharField(max_length=200)),
                ('special', models.BooleanField(default=False)),
            ],
            options={
                'permissions': (('can_alert', 'Use the alerts system.'), ('alert_admin', 'Modify alert groups and rosters.'), ('can_ping_special', 'Ping alert groups tagged special.')),
            },
        ),
        migrations.CreateModel(
            name='SubscriptionGroupPermission',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('can_broadcast', models.BooleanField(default=False)),
                ('can_join', models.BooleanField(default=False)),
                ('sub_group', models.ForeignKey(related_name='group_permissions', to='Alerts.SubscriptionGroup')),
                ('user_group', models.ForeignKey(related_name='alert_groups', to='auth.Group')),
            ],
        ),
    ]
