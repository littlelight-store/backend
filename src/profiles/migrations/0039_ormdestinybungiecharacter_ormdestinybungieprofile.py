# Generated by Django 3.0.8 on 2020-11-16 12:51

from django.db import migrations, models
import django.db.models.deletion
import profiles.constants


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0038_boosteruser_discord_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='ORMDestinyBungieProfile',
            fields=[
                ('membership_id', models.CharField(max_length=500, primary_key=True, serialize=False)),
                ('membership_type', models.IntegerField(choices=[(4, profiles.constants.Membership['BattleNET']), (2, profiles.constants.Membership['PS4']), (3, profiles.constants.Membership['Steam']), (1, profiles.constants.Membership['BattleNET'])])),
                ('username', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'db_table': 'destiny_bungie_profile',
            },
        ),
        migrations.CreateModel(
            name='ORMDestinyBungieCharacter',
            fields=[
                ('character_id', models.CharField(max_length=256, primary_key=True, serialize=False)),
                ('character_class', models.IntegerField(choices=[(2, profiles.constants.CharacterClasses['warlock']), (0, profiles.constants.CharacterClasses['titan']), (1, profiles.constants.CharacterClasses['hunter'])])),
                ('bungie_profile', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='destiny_character', to='profiles.BungieID')),
            ],
            options={
                'db_table': 'destiny_bungie_character',
            },
        ),
    ]
