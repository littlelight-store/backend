# Generated by Django 3.0.8 on 2020-12-09 18:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0066_auto_20201209_1830'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ormclientorder',
            name='comment',
            field=models.TextField(blank=True, default='', null=True),
        ),
    ]
