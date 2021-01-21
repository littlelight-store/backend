# Generated by Django 2.1 on 2019-02-24 22:55

import django.contrib.sites.managers
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
        ('services', '0018_category_sites'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='category',
            managers=[
                ('on_site', django.contrib.sites.managers.CurrentSiteManager()),
            ],
        ),
        migrations.RemoveField(
            model_name='category',
            name='sites',
        ),
        migrations.AddField(
            model_name='category',
            name='site',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='categories', to='sites.Site'),
        ),
    ]