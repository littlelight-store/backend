# Generated by Django 3.0.8 on 2020-11-23 18:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0061_auto_20201123_1815'),
    ]

    operations = [
        migrations.RenameField(
            model_name='ormorderobjective',
            old_name='client_order_id',
            new_name='client_order',
        ),
        migrations.RenameField(
            model_name='ormorderobjective',
            old_name='service_slug',
            new_name='service',
        ),
    ]
