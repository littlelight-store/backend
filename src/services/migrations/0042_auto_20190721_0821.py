# Generated by Django 2.1 on 2019-07-21 08:21

from django.db import migrations


existing_seasons = [
    {
        'name': 'Forsaken',
        'slug': 'forsaken',
    },

    {
        'name': 'Black armory',
        'slug': 'black-armory',
    },

    {
        'name': 'Curse of Osiris',
        'slug': 'curse-of-osiris',
    },

    {
        'name': 'Season of opulence',
        'slug': 'opulence',
    },

    {
        'name': 'Season of the drifter',
        'slug': 'drifter',
    },

    {
        'name': 'Warmind',
        'slug': 'warmind',
    },
]


def combine_names(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Season = apps.get_model('services', 'Season')

    for season in existing_seasons:
        Season.objects.create(
            **season
        )


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0041_auto_20190720_1716'),
    ]

    operations = [
        migrations.RunPython(combine_names)
    ]
