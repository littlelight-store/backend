# Generated by Django 2.1 on 2019-06-18 15:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0033_auto_20190618_1549'),
    ]

    operations = [
        migrations.RenameField(
            model_name='serviceconfig',
            old_name='discounted_price',
            new_name='old_price',
        ),
    ]
