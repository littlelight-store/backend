# Generated by Django 2.1 on 2019-06-16 11:20

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0028_service_keywords'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='extra_configs',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict),
        ),
    ]
