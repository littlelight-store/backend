# Generated by Django 2.1 on 2019-09-08 10:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0045_service_extra_categories'),
        ('reviews', '0008_auto_20190728_0813'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='is_posted',
            field=models.BooleanField(default=False),
        ),
    ]
