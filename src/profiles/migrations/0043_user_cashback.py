# Generated by Django 3.0.8 on 2021-02-17 19:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0042_auto_20210116_1955'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='cashback',
            field=models.DecimalField(decimal_places=2, default=0, help_text='Cashback balance', max_digits=10),
        ),
    ]
