# Generated by Django 2.1 on 2019-06-18 15:49

import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0032_auto_20190616_1405'),
    ]

    operations = [
        migrations.RenameField(
            model_name='serviceconfig',
            old_name='additional_info',
            new_name='description',
        ),
        migrations.RenameField(
            model_name='serviceconfig',
            old_name='mode_name',
            new_name='title',
        ),
        migrations.RemoveField(
            model_name='serviceconfig',
            name='is_inner_only',
        ),
        migrations.AddField(
            model_name='serviceconfig',
            name='extra_configs',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
        ),
    ]