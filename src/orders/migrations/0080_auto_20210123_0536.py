# Generated by Django 3.0.8 on 2021-01-23 05:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0079_auto_20210118_1929'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ormshoppingcart',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='ormshoppingcartitem',
            options={'ordering': ['-created_at']},
        ),
    ]
