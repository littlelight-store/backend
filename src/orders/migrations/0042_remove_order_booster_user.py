# Generated by Django 2.1 on 2019-10-13 08:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0041_auto_20191012_1904'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='order',
            name='booster_user',
        ),
    ]
