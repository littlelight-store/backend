# Generated by Django 3.0.8 on 2021-02-21 09:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0045_auto_20210221_0919'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ormdestinybungieprofile',
            name='client_id',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='bungie_profile', to=settings.AUTH_USER_MODEL),
        ),
    ]
