# Generated by Django 2.1 on 2019-09-21 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0038_remove_order_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='status',
            field=models.CharField(blank=True, choices=[('is_checking_payment', 'is_checking_payment'), ('waiting_for_booster', 'waiting_for_booster'), ('in_progress', 'in_progress'), ('attempt_authorization', 'attempt_authorization'), ('paused', 'paused'), ('pending_approval', 'pending_approval'), ('is_complete', 'is_complete')], db_index=True, default='is_checking_payment', max_length=28),
        ),
    ]
