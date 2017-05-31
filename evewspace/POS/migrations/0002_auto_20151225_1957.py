# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('POS', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('API', '0002_auto_20151225_1957'),
        ('Map', '0002_auto_20151225_1957'),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='posvote',
            name='voter',
            field=models.ForeignKey(related_name='posvotes', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='posapplication',
            name='applicant',
            field=models.ForeignKey(related_name='posapps', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='posapplication',
            name='residents',
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='posapplication',
            name='towertype',
            field=models.ForeignKey(related_name='posapps', blank=True, to='core.Type', null=True),
        ),
        migrations.AddField(
            model_name='pos',
            name='corporation',
            field=models.ForeignKey(related_name='poses', to='core.Corporation'),
        ),
        migrations.AddField(
            model_name='pos',
            name='system',
            field=models.ForeignKey(related_name='poses', to='Map.System'),
        ),
        migrations.AddField(
            model_name='pos',
            name='towertype',
            field=models.ForeignKey(related_name='inspace', to='core.Type'),
        ),
        migrations.AddField(
            model_name='posapplication',
            name='posrecord',
            field=models.ForeignKey(related_name='application', blank=True, to='POS.CorpPOS', null=True),
        ),
        migrations.AddField(
            model_name='corppos',
            name='apikey',
            field=models.ForeignKey(related_name='poses', blank=True, to='API.CorpAPIKey', null=True),
        ),
        migrations.AddField(
            model_name='corppos',
            name='manager',
            field=models.ForeignKey(related_name='poses', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
    ]
