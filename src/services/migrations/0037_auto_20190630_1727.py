# Generated by Django 2.1 on 2019-06-30 17:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('services', '0036_auto_20190618_2056'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='background_image',
            field=models.ImageField(blank=True, upload_to='uploaded_images_bg'),
        ),
        migrations.AddField(
            model_name='service',
            name='background_image',
            field=models.ImageField(blank=True, upload_to='uploaded_images_bg'),
        ),
    ]
