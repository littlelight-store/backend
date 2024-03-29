# Generated by Django 3.0.8 on 2021-02-06 19:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0082_ormorderobjective_created_at'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='ormclientorder',
            options={'ordering': ['-created_at']},
        ),
        migrations.AlterModelOptions(
            name='ormorderobjective',
            options={'ordering': ['-created_at']},
        ),
        migrations.RemoveField(
            model_name='chatmessage',
            name='order',
        ),
        migrations.RemoveField(
            model_name='chatmessage',
            name='username',
        ),
        migrations.AddField(
            model_name='chatmessage',
            name='objective_id',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='orders.ORMOrderObjective'),
        ),
    ]
