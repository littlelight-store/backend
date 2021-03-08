# Generated by Django 3.0.8 on 2021-02-21 09:17

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0043_user_cashback'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='booster_profile',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user', to='profiles.BoosterUser'),
        ),
        migrations.AlterField(
            model_name='user',
            name='cashback',
            field=models.DecimalField(blank=True, decimal_places=2, default=0, help_text='Cashback balance', max_digits=10),
        ),
    ]
