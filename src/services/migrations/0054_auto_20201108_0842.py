# Generated by Django 3.0.8 on 2020-11-08 08:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0053_auto_20201108_0830'),
    ]

    operations = [
        migrations.RenameField(
            model_name='service',
            old_name='configuration_options',
            new_name='configuration_type',
        ),
    ]
