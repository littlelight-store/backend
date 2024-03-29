# Generated by Django 2.1 on 2019-10-27 10:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0048_auto_20191023_1644'),
    ]

    operations = [
        migrations.AddField(
            model_name='chatmessage',
            name='is_seen',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(blank=True, choices=[('is_checking_payment', 'is_checking_payment'), ('waiting_for_booster', 'waiting_for_booster'), ('in_progress', 'in_progress'), ('attempt_authorization', 'attempt_authorization'), ('two_factor_code_required', 'two_factor_code_required'), ('cant_sign_in', 'cant_sign_in'), ('paused', 'paused'), ('pending_approval', 'pending_approval'), ('is_complete', 'is_complete')], db_index=True, default='is_checking_payment', max_length=28),
        ),
    ]
