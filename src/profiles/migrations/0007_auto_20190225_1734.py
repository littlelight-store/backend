# Generated by Django 2.1 on 2019-02-25 17:34

import django.contrib.auth.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0016_remove_order_booster_user'),
        ('profiles', '0006_auto_20190225_1706'),
    ]

    operations = [
        migrations.CreateModel(
            name='BoosterUser',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('telegram', models.CharField(help_text='Booster telegram', max_length=100)),
                ('rating', models.IntegerField(default=0, help_text='User rating')),
                ('platforms', models.ManyToManyField(help_text='Booster platforms', related_name='boosters', to='profiles.Platform')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            bases=('profiles.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.RemoveField(
            model_name='boosterconfig',
            name='platforms',
        ),
        migrations.RemoveField(
            model_name='user',
            name='booster_config',
        ),
        migrations.RemoveField(
            model_name='user',
            name='is_booster',
        ),
        migrations.DeleteModel(
            name='BoosterConfig',
        ),
    ]
