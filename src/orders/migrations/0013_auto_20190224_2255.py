# Generated by Django 2.1 on 2019-02-24 22:55

import django.contrib.sites.managers
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('orders', '0012_order_bungie_profile'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='order',
            managers=[
                ('on_site', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orders', to='sites.Site'),
        ),
    ]
