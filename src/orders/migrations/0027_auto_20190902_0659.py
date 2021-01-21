# Generated by Django 2.1 on 2019-09-02 06:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0026_auto_20190902_0653'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='total_price',
            field=models.DecimalField(blank=True, db_index=True, decimal_places=4, max_digits=10, null=True),
        ),
    ]
