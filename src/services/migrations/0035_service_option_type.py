# Generated by Django 2.1 on 2019-06-18 18:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0034_auto_20190618_1553'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='option_type',
            field=models.CharField(default='single', max_length=128),
            preserve_default=False,
        ),
    ]
