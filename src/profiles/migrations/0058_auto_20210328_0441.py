# Generated by Django 3.0.8 on 2021-03-28 04:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0057_auto_20210320_1232'),
    ]

    operations = [
        migrations.AddField(
            model_name='ormnotificationstoken',
            name='deactivated_at',
            field=models.DateTimeField(default=None, null=True),
        ),
        migrations.AddField(
            model_name='ormnotificationstoken',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]