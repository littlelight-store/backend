# Generated by Django 2.1 on 2019-09-14 08:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0031_auto_20190913_1711'),
    ]

    operations = [
        migrations.AddField(
            model_name='parentorder',
            name='is_complete',
            field=models.BooleanField(default=False),
        ),
    ]