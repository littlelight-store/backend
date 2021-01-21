# Generated by Django 3.0.8 on 2021-01-14 14:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0078_auto_20210112_1816'),
        ('reviews', '0018_review_client_order'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='client_order',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='review', related_query_name='review', to='orders.ORMClientOrder'),
        ),
    ]