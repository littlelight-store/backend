# Generated by Django 2.1 on 2019-02-25 17:02

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0004_auto_20190225_1702'),
        ('orders', '0013_auto_20190224_2255'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='booster_user',
            field=models.ForeignKey(blank=True, help_text='Booster set for current order', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='booster_orders', to='profiles.BoosterConfig'),
        ),
    ]