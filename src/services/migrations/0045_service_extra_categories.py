# Generated by Django 2.1 on 2019-08-29 16:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0044_auto_20190728_0541'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='extra_categories',
            field=models.ManyToManyField(to='services.Category'),
        ),
    ]