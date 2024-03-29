# Generated by Django 2.1 on 2019-11-23 12:42

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("pages", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="gamepage",
            name="block_1",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="block_1",
                to="pages.PromotedBlock",
            ),
        ),
        migrations.AlterField(
            model_name="gamepage",
            name="block_2",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="block_2",
                to="pages.PromotedBlock",
            ),
        ),
        migrations.AlterField(
            model_name="gamepage",
            name="offer",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="pages",
                to="pages.LimitedOffer",
            ),
        ),
        migrations.AlterField(
            model_name="gamepage",
            name="service_of_the_week",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="service_of_the_week",
                to="pages.ServiceOfTheWeek",
            ),
        ),
    ]
