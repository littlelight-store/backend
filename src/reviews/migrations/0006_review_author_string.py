# Generated by Django 2.1 on 2019-07-28 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0005_auto_20190720_1828'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='author_string',
            field=models.CharField(blank=True, max_length=128, null=True),
        ),
    ]