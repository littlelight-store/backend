# Generated by Django 2.1 on 2019-02-02 15:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_auto_20190202_1440'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='service',
            new_name='service_config',
        ),
    ]
