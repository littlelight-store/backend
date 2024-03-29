# Generated by Django 2.1 on 2019-09-12 21:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0029_auto_20190902_0705'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(blank=True, choices=[('is_checking', 1), ('is_payed', 2), ('is_taken_by_booster', 3), ('is_returned_by_booster', 4), ('is_complete', 5)], db_index=True, max_length=28, null=True),
        ),
    ]
