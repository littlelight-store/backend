# Generated by Django 3.0.8 on 2020-12-10 19:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0040_auto_20201116_1255'),
        ('orders', '0067_auto_20201209_1834'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ormshoppingcartitem',
            name='bungie_profile',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_items', to='profiles.ORMDestinyBungieProfile'),
        ),
        migrations.AlterField(
            model_name='ormshoppingcartitem',
            name='shopping_cart',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cart_items', to='orders.ORMShoppingCart'),
        ),
    ]