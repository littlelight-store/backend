# Generated by Django 3.0.8 on 2021-01-12 18:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0064_service_eta'),
        ('orders', '0077_auto_20210111_1847'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ormorderobjective',
            name='service',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_objectives', related_query_name='order_objectives', to='services.Service'),
        ),
    ]
