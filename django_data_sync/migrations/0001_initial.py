# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='SyncAppModel',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('app_model', models.CharField(max_length=255)),
                ('description', models.TextField(default=b'', blank=True)),
                ('last_sync_date', models.DateTimeField(null=True, blank=True)),
                ('last_sync_status', models.CharField(default=b'', max_length=255, blank=True)),
                ('get_elements_class_path', models.CharField(default=b'django_data_sync.getters.APIJson', max_length=255)),
                ('get_elements_data_json', jsonfield.fields.JSONField(default={})),
                ('load_elements_class_path', models.CharField(default=b'django_data_sync.loaders.Base', max_length=255)),
                ('load_elements_data_json', jsonfield.fields.JSONField(default={})),
                ('requires', models.ManyToManyField(to='django_data_sync.SyncAppModel', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
