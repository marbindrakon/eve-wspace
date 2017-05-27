# -*- coding: utf-8 -*-


from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0001_initial'),
        ('auth', '0006_require_contenttypes_0002'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='apigroupmapping',
            name='corp',
            field=models.ForeignKey(related_name='api_mappings', to='core.Corporation'),
        ),
        migrations.AddField(
            model_name='apigroupmapping',
            name='group',
            field=models.ForeignKey(related_name='api_mappings', to='auth.Group'),
        ),
        migrations.AddField(
            model_name='apiaccesstype',
            name='call_group',
            field=models.ForeignKey(related_name='calls', to='API.APIAccessGroup'),
        ),
        migrations.AddField(
            model_name='apiaccessrequirement',
            name='corps_required',
            field=models.ManyToManyField(related_name='api_requirements', null=True, to='core.Corporation'),
        ),
        migrations.AddField(
            model_name='apiaccessrequirement',
            name='groups_required',
            field=models.ManyToManyField(related_name='api_requirements', null=True, to='auth.Group'),
        ),
        migrations.AddField(
            model_name='apiaccessrequirement',
            name='requirement',
            field=models.ForeignKey(related_name='required_by', to='API.APIAccessType'),
        ),
        migrations.AddField(
            model_name='memberapikey',
            name='user',
            field=models.ForeignKey(related_name='api_keys', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='corpapikey',
            name='corp',
            field=models.ForeignKey(related_name='api_keys', to='core.Corporation'),
        ),
        migrations.AddField(
            model_name='corpapikey',
            name='user',
            field=models.ForeignKey(related_name='corp_api_keys', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='apicharacter',
            name='apikey',
            field=models.ForeignKey(related_name='characters', to='API.MemberAPIKey', null=True),
        ),
    ]
