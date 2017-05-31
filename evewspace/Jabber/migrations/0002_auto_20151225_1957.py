# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('Jabber', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='jabbersubscription',
            name='user',
            field=models.ForeignKey(related_name='jabber_subs', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='jabberaccount',
            name='user',
            field=models.ForeignKey(related_name='jabber_accounts', to=settings.AUTH_USER_MODEL),
        ),
    ]
