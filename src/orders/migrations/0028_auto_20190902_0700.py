# Generated by Django 2.1 on 2019-09-02 07:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0027_auto_20190902_0659'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='total_price',
            field=models.FloatField(blank=True, db_index=True, null=True),
        ),
    ]