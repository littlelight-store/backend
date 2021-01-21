# Generated by Django 3.0.8 on 2020-11-13 20:01

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0054_auto_20201108_0842'),
    ]

    operations = [
        migrations.AddField(
            model_name='serviceconfig',
            name='extra_configs_v2',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='serviceconfig',
            name='extra_configs_v2_version',
            field=models.CharField(default='0.0.1', max_length=10),
        ),
    ]
