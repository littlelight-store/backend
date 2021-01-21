# Generated by Django 2.1 on 2020-05-12 13:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0035_auto_20191022_1745'),
    ]

    operations = [
        migrations.CreateModel(
            name='Direction',
            fields=[
                ('slug', models.SlugField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.AddField(
            model_name='boosteruser',
            name='directions',
            field=models.ManyToManyField(blank=True, to='profiles.Direction'),
        ),
    ]
