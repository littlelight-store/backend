# Generated by Django 3.0.8 on 2021-01-09 12:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0063_auto_20210107_1802'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='eta',
            field=models.CharField(default='1 day', max_length=20),
        ),
    ]
