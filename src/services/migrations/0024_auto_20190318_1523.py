# Generated by Django 2.1 on 2019-03-18 15:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0023_service_show_discount'),
    ]

    operations = [
        migrations.AddField(
            model_name='pvpthreshold',
            name='card_unit',
            field=models.CharField(blank=True, help_text='Unit for card price (for example: $4/1 ${"win"}', max_length=128, null=True),
        ),
        migrations.AddField(
            model_name='pvpthreshold',
            name='points_unit',
            field=models.CharField(blank=True, help_text='Unit for points in modal (for example: ${"DZ Level"} X > ${"DZ Level"} Y', max_length=128, null=True),
        ),
    ]
