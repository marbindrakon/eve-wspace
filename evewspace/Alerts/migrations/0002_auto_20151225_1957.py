# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('Alerts', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriptiongroup',
            name='members',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='Alerts.Subscription'),
        ),
        migrations.AddField(
            model_name='subscription',
            name='group',
            field=models.ForeignKey(to='Alerts.SubscriptionGroup'),
        ),
        migrations.AddField(
            model_name='subscription',
            name='user',
            field=models.ForeignKey(related_name='alert_groups', to=settings.AUTH_USER_MODEL),
        ),
    ]
