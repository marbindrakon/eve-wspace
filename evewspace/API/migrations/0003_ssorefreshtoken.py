# -*- coding: utf-8 -*-


from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('API', '0002_auto_20151225_1957'),
    ]

    operations = [
        migrations.CreateModel(
            name='SSORefreshToken',
            fields=[
                ('char_id', models.IntegerField(serialize=False, primary_key=True)),
                ('char_name', models.CharField(max_length=255)),
                ('refresh_token', models.CharField(max_length=255)),
                ('access_token', models.CharField(max_length=255)),
                ('valid_until', models.DateTimeField()),
                ('user', models.ForeignKey(related_name='crest_refresh_tokens', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
