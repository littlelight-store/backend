# Generated by Django 3.0.8 on 2020-11-15 12:29

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0038_boosteruser_discord_id'),
        ('orders', '0055_auto_20200507_1422'),
    ]

    operations = [
        migrations.CreateModel(
            name='ORMShoppingCart',
            fields=[
                ('id', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('fetched_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('is_deleted', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='ORMShoppingCartItem',
            fields=[
                ('id', models.CharField(max_length=64, primary_key=True, serialize=False)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('bungie_profile', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='profiles.BungieID')),
                ('character', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='profiles.UserCharacter')),
                ('shopping_cart', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.ORMShoppingCart')),
            ],
        ),
    ]
