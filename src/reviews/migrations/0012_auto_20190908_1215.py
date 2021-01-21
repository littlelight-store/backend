# Generated by Django 2.1 on 2019-09-08 12:15

from django.db import migrations


def migrate_service_to_services(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Review = apps.get_model('reviews', 'Review')

    for review in Review.objects.all():
        review.services.add(review.service)
        review.is_posted = True
        review.save()


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0011_review_services'),
    ]

    operations = [
        migrations.RunPython(migrate_service_to_services),
    ]