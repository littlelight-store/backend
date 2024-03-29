# Generated by Django 2.1 on 2019-09-09 04:00
import uuid

from django.db import migrations


def add_edit_token_to_review(apps, schema_editor):
    # We can't import the Person model directly as it may be a newer
    # version than this migration expects. We use the historical version.
    Review = apps.get_model('reviews', 'Review')

    for review in Review.objects.all():
        review.edit_token = uuid.uuid4().hex
        review.save()


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0016_review_is_anonymous'),
    ]

    operations = [
        migrations.RunPython(add_edit_token_to_review)
    ]
