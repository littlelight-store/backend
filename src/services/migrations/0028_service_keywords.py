# Generated by Django 2.1 on 2019-04-02 14:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0027_auto_20190318_2131'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='keywords',
            field=models.TextField(blank=True, default=''),
        ),
    ]
