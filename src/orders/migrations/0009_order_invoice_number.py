# Generated by Django 2.1 on 2019-02-13 07:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0008_auto_20190212_2222'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='invoice_number',
            field=models.CharField(blank=True, db_index=True, max_length=128, null=True),
        ),
    ]
