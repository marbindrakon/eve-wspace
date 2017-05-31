# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Alerts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SlackChannel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('channel', models.CharField(unique=True, max_length=50)),
                ('token', models.CharField(max_length=50)),
                ('group', models.ForeignKey(related_name='slack_groups', to='Alerts.SubscriptionGroup', unique=True)),
            ],
        ),
    ]
