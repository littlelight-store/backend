# Generated by Django 2.1 on 2019-10-20 08:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0033_auto_20191015_1657'),
    ]

    operations = [
        migrations.AddField(
            model_name='boosteruser',
            name='total_orders_base',
            field=models.IntegerField(default=0, help_text='Базовое число к которому сумируются кол-во заказов в сервисе'),
        ),
    ]
