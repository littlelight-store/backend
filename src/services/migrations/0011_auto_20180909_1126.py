# Generated by Django 2.1 on 2018-09-09 11:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0010_promocode_comment'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'ordering': ['ordering'], 'verbose_name': 'Category', 'verbose_name_plural': 'Categories'},
        ),
        migrations.AlterModelOptions(
            name='service',
            options={'ordering': ['ordering']},
        ),
        migrations.AddField(
            model_name='category',
            name='ordering',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='service',
            name='ordering',
            field=models.IntegerField(default=0),
        ),
    ]
