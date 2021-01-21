# Generated by Django 2.1 on 2019-06-16 11:25

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0029_service_extra_configs'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='service',
            name='approx_time',
        ),
        migrations.RemoveField(
            model_name='service',
            name='layout',
        ),
        migrations.RemoveField(
            model_name='service',
            name='level_requirement',
        ),
        migrations.RemoveField(
            model_name='service',
            name='select_many_modes',
        ),
        migrations.RemoveField(
            model_name='service',
            name='short_description',
        ),
        migrations.RemoveField(
            model_name='service',
            name='show_discount',
        ),
        migrations.AlterField(
            model_name='service',
            name='description',
            field=models.TextField(blank=True, help_text='On product page', null=True),
        ),
        migrations.AlterField(
            model_name='service',
            name='extra_configs',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
        ),
    ]