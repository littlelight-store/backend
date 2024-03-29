# Generated by Django 2.1 on 2019-10-12 18:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0021_auto_20191012_1854'),
    ]

    operations = [
        migrations.CreateModel(
            name='Platform',
            fields=[
                ('name', models.CharField(max_length=10)),
                ('value', models.IntegerField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.AddField(
            model_name='boosteruser',
            name='platforms',
            field=models.ManyToManyField(help_text='Booster platforms', related_name='boosters', to='profiles.Platform'),
        ),
    ]
