# Generated by Django 2.1 on 2019-03-16 19:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0009_auto_20190304_1132'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profilecredentials',
            name='membership',
        ),
        migrations.AddField(
            model_name='profilecredentials',
            name='owner',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='credentails', to=settings.AUTH_USER_MODEL),
        ),
    ]
