# Generated by Django 2.1 on 2018-12-08 02:30

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0013_auto_20181208_0226'),
    ]

    operations = [
        migrations.AlterField(
            model_name='serviceconfigpvp',
            name='service',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='services.Service'),
        ),
    ]
