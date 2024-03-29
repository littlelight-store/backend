# Generated by Django 2.1 on 2019-10-13 08:18

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0029_auto_20191013_0818'),
        ('orders', '0042_remove_order_booster_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='booster_user',
            field=models.ForeignKey(blank=True, help_text='Booster set for current order', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='booster_orders', to='profiles.BoosterUser'),
        ),
    ]
