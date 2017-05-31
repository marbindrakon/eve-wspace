# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Slack', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='slackchannel',
            name='group',
            field=models.OneToOneField(related_name='slack_groups', to='Alerts.SubscriptionGroup'),
        ),
    ]
