# Generated by Django 2.1 on 2019-04-04 16:39

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0020_remove_parentorder_profile_credentials'),
        ('profiles', '0011_auto_20190404_1617'),
    ]

    operations = [
        migrations.AddField(
            model_name='profilecredentials',
            name='parent_order',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='profile_credentials', to='orders.ParentOrder'),
        ),
    ]
