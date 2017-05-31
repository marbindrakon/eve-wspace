# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='APIAccessGroup',
            fields=[
                ('group_id', models.IntegerField(serialize=False, primary_key=True)),
                ('group_name', models.CharField(max_length=255)),
                ('group_description', models.TextField(null=True, blank=True)),
            ],
        ),
        migrations.CreateModel(
            name='APIAccessRequirement',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
            ],
        ),
        migrations.CreateModel(
            name='APIAccessType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('call_type', models.IntegerField(choices=[(1, b'Character'), (2, b'Corporation')])),
                ('call_name', models.CharField(max_length=255)),
                ('call_description', models.TextField(null=True, blank=True)),
                ('call_mask', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='APICharacter',
            fields=[
                ('charid', models.BigIntegerField(serialize=False, primary_key=True)),
                ('name', models.CharField(max_length=100, null=True, blank=True)),
                ('corp', models.CharField(max_length=100, null=True, blank=True)),
                ('alliance', models.CharField(max_length=100, null=True, blank=True)),
                ('lastshipname', models.CharField(max_length=100, null=True, blank=True)),
                ('lastshiptype', models.CharField(max_length=100, null=True, blank=True)),
                ('location', models.CharField(max_length=100, null=True, blank=True)),
                ('visible', models.NullBooleanField(default=False)),
            ],
            options={
                'permissions': (('view_limited_data', 'View limited character API.'), ('view_full_data', 'View full character API.')),
            },
        ),
        migrations.CreateModel(
            name='APIGroupMapping',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('title_id', models.IntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='APIKey',
            fields=[
                ('keyid', models.IntegerField(serialize=False, primary_key=True)),
                ('vcode', models.CharField(max_length=100)),
                ('valid', models.BooleanField(default=False)),
                ('lastvalidated', models.DateTimeField()),
                ('access_mask', models.IntegerField()),
                ('proxykey', models.CharField(max_length=100, null=True, blank=True)),
                ('validation_error', models.CharField(max_length=255, null=True, blank=True)),
            ],
            options={
                'permissions': (('api_key_admin', 'Can see API Key section.'), ('add_keys', 'Add API keys for others.'), ('purge_keys', 'Purge API Keys.'), ('audit_keys', 'View Users with no API keys assigned.'), ('soft_key_fail', 'Nag if no valid API key.'), ('hard_key_fail', 'Revoke access if no valid API Key.')),
            },
        ),
        migrations.CreateModel(
            name='APIShipLog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('timestamp', models.DateTimeField()),
                ('shiptype', models.CharField(max_length=100)),
                ('shipname', models.CharField(max_length=100)),
                ('location', models.CharField(max_length=100)),
                ('character', models.ForeignKey(related_name='shiplogs', to='API.APICharacter')),
            ],
            options={
                'permissions': (('view_shiplogs', 'View API ship log entries.'),),
            },
        ),
        migrations.CreateModel(
            name='CorpAPIKey',
            fields=[
                ('apikey_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='API.APIKey')),
                ('character_name', models.CharField(max_length=255, null=True, blank=True)),
            ],
            bases=('API.apikey',),
        ),
        migrations.CreateModel(
            name='MemberAPIKey',
            fields=[
                ('apikey_ptr', models.OneToOneField(parent_link=True, auto_created=True, primary_key=True, serialize=False, to='API.APIKey')),
            ],
            bases=('API.apikey',),
        ),
    ]
