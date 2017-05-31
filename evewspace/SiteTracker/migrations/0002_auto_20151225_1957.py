# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('SiteTracker', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('Map', '0002_auto_20151225_1957'),
    ]

    operations = [
        migrations.CreateModel(
            name='SystemWeight',
            fields=[
                ('system', models.OneToOneField(related_name='st_weight', primary_key=True, serialize=False, to='Map.System')),
                ('weight', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='UserLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('jointime', models.DateTimeField(auto_now_add=True)),
                ('leavetime', models.DateTimeField(null=True, blank=True)),
                ('fleet', models.ForeignKey(related_name='members', to='SiteTracker.Fleet')),
                ('user', models.ForeignKey(related_name='sitetrackerlogs', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserSite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('pending', models.BooleanField(default=False)),
                ('site', models.ForeignKey(related_name='members', to='SiteTracker.SiteRecord')),
                ('user', models.ForeignKey(related_name='sites', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='siteweight',
            name='site_type',
            field=models.ForeignKey(related_name='weights', to='SiteTracker.SiteType'),
        ),
        migrations.AddField(
            model_name='siterecord',
            name='boss',
            field=models.ForeignKey(related_name='sitescredited', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='siterecord',
            name='fleet',
            field=models.ForeignKey(related_name='sites', to='SiteTracker.Fleet'),
        ),
        migrations.AddField(
            model_name='siterecord',
            name='site_type',
            field=models.ForeignKey(related_name='sitesrun', to='SiteTracker.SiteType'),
        ),
        migrations.AddField(
            model_name='siterecord',
            name='system',
            field=models.ForeignKey(related_name='sitescompleted', to='Map.System'),
        ),
        migrations.AddField(
            model_name='payoutreport',
            name='createdby',
            field=models.ForeignKey(related_name='payoutreports', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='payoutreport',
            name='period',
            field=models.ForeignKey(related_name='reports', to='SiteTracker.ClaimPeriod'),
        ),
        migrations.AddField(
            model_name='payoutentry',
            name='claim',
            field=models.ForeignKey(related_name='payout', to='SiteTracker.Claim'),
        ),
        migrations.AddField(
            model_name='payoutentry',
            name='report',
            field=models.ForeignKey(related_name='entries', to='SiteTracker.PayoutReport'),
        ),
        migrations.AddField(
            model_name='payoutentry',
            name='user',
            field=models.ForeignKey(related_name='payouts', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='fleet',
            name='current_boss',
            field=models.ForeignKey(related_name='currently_bossing', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='fleet',
            name='initial_boss',
            field=models.ForeignKey(related_name='bossfleets', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='fleet',
            name='roles_needed',
            field=models.ManyToManyField(related_name='fleets_need', to='SiteTracker.SiteRole'),
        ),
        migrations.AddField(
            model_name='fleet',
            name='system',
            field=models.ForeignKey(related_name='stfleets', to='Map.System'),
        ),
        migrations.AddField(
            model_name='claimperiod',
            name='loothauledby',
            field=models.ForeignKey(related_name='loothauled', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='claimperiod',
            name='lootsoldby',
            field=models.ForeignKey(related_name='lootsold', blank=True, to=settings.AUTH_USER_MODEL, null=True),
        ),
        migrations.AddField(
            model_name='claim',
            name='period',
            field=models.ForeignKey(related_name='claims', to='SiteTracker.ClaimPeriod'),
        ),
        migrations.AddField(
            model_name='claim',
            name='user',
            field=models.ForeignKey(related_name='claims', to=settings.AUTH_USER_MODEL),
        ),
    ]
