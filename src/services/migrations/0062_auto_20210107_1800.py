# Generated by Django 3.0.8 on 2021-01-07 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0061_auto_20210107_1759'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='servicegrouptagorm',
            options={'ordering': ['ordering'], 'verbose_name': 'Main Page Group Tag', 'verbose_name_plural': 'Main Page Group tags'},
        ),
        migrations.AddField(
            model_name='servicegrouptagorm',
            name='ordering',
            field=models.IntegerField(default=0),
        ),
    ]
