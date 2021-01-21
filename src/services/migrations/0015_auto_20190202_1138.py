# Generated by Django 2.1 on 2019-02-02 11:38

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0014_auto_20181208_0230'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pvpthreshold',
            name='config',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='threshold_configs', to='services.ServiceConfigPvp'),
        ),
        migrations.AlterField(
            model_name='serviceconfigpvp',
            name='service',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='pvp_config', to='services.Service'),
        ),
    ]
