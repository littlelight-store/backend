# Generated by Django 3.0.8 on 2021-01-18 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0078_auto_20210112_1816'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ormclientorder',
            name='cart',
        ),
        migrations.AddField(
            model_name='ormclientorder',
            name='order_id',
            field=models.CharField(db_index=True, max_length=128, null=True),
        ),
    ]
