# Generated by Django 2.1 on 2019-10-31 17:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0046_serviceconfig_booster_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='serviceconfig',
            name='booster_price',
        ),
        migrations.AddField(
            model_name='service',
            name='booster_price',
            field=models.DecimalField(decimal_places=0, default=0, max_digits=5),
        ),
    ]
