# Generated by Django 2.1 on 2019-07-20 18:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0004_auto_20190720_1827'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='service',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='reviews', related_query_name='reviews', to='services.Service'),
        ),
    ]
