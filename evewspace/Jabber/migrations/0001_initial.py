# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Alerts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='JabberAccount',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('jid', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='JabberSubscription',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('group', models.ForeignKey(related_name='jabber_subs', to='Alerts.SubscriptionGroup')),
            ],
        ),
    ]
