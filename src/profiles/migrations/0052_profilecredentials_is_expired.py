# Generated by Django 3.0.8 on 2021-03-06 12:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0051_auto_20210222_1620'),
    ]

    operations = [
        migrations.AddField(
            model_name='profilecredentials',
            name='is_expired',
            field=models.BooleanField(default=False),
        ),
    ]
