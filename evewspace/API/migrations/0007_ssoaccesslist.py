# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
        ('API', '0006_auto_20161223_1751'),
    ]

    operations = [
        migrations.CreateModel(
            name='SSOAccessList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('char_id', models.IntegerField(null=True)),
                ('char_name', models.CharField(max_length=255)),
                ('corp', models.OneToOneField(related_name='access_list_corp', null=True, to='core.Corporation')),
            ],
        ),
    ]
