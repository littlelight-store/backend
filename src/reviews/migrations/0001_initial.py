# Generated by Django 2.1 on 2019-07-20 18:01

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orders', '0021_parentorder_is_seen'),
        ('services', '0041_auto_20190720_1716'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rate', models.IntegerField(help_text='From 1 to 5', validators=[django.core.validators.MaxValueValidator(5), django.core.validators.MinValueValidator(1)])),
                ('text', models.TextField(default='')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_edited', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='authors', related_query_name='authors', to=settings.AUTH_USER_MODEL)),
                ('order', models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='orders.ParentOrder')),
                ('service', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services', related_query_name='services', to='services.Service')),
            ],
        ),
    ]
