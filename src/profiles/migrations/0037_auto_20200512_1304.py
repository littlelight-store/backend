# Generated by Django 2.1 on 2020-05-12 13:04

from django.db import migrations


def make_directions(apps, schema_editor):
    Direction = apps.get_model('profiles', 'Direction')

    directions = ['PvP', 'PvE']

    for direction in directions:
        Direction.objects.create(slug=direction)


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0036_auto_20200512_1303'),
    ]

    operations = [
        migrations.RunPython(make_directions)
    ]