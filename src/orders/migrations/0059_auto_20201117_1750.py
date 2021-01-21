# Generated by Django 3.0.8 on 2020-11-17 17:50

from django.db import migrations, models
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0055_auto_20201113_2001'),
        ('orders', '0058_auto_20201116_1251'),
    ]

    operations = [
        migrations.AddField(
            model_name='ormshoppingcartitem',
            name='range_options',
            field=jsonfield.fields.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='ormshoppingcartitem',
            name='selected_options',
            field=models.ManyToManyField(related_name='cart_items', to='services.ServiceConfig'),
        ),
    ]
