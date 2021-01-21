# Generated by Django 3.0.8 on 2021-01-07 18:02

from django.db import migrations


def reorder(apps, schema_editor):
    ServiceGroupTagORM = apps.get_model("services", "ServiceGroupTagORM")
    order = 0
    for item in ServiceGroupTagORM.objects.all():
        order += 1
        item.ordering = order
        item.save()


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0062_auto_20210107_1800'),
    ]

    operations = [
        migrations.RunPython(reorder)
    ]
