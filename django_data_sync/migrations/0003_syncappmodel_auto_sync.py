# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('django_data_sync', '0002_auto_20160423_1118'),
    ]

    operations = [
        migrations.AddField(
            model_name='syncappmodel',
            name='auto_sync',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
