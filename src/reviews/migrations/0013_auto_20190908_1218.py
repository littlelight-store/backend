# Generated by Django 2.1 on 2019-09-08 12:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0012_auto_20190908_1215'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='review',
            name='service',
        ),
        migrations.AlterField(
            model_name='review',
            name='services',
            field=models.ManyToManyField(related_name='reviews', related_query_name='reviews', to='services.Service'),
        ),
    ]
