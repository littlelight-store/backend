# Generated by Django 3.0.8 on 2021-02-07 18:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('orders', '0083_auto_20210206_1945'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='chatmessage',
            name='role',
        ),
        migrations.RemoveField(
            model_name='chatmessage',
            name='user',
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='receiver',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='receiver_chat_messages', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='sender',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='sender_chat_messages', to=settings.AUTH_USER_MODEL),
        ),
    ]
