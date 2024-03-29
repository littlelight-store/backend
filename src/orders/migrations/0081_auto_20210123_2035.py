# Generated by Django 3.0.8 on 2021-01-23 20:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0080_auto_20210123_0536'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ormclientorder',
            name='order_status',
            field=models.CharField(choices=[('AWAIT_PAYMENT', 'AWAIT_PAYMENT'), ('PAYED', 'PAYED'), ('PENDING_APPROVAL', 'PENDING_APPROVAL'), ('COMPLETE', 'COMPLETE')], default='AWAIT_PAYMENT', max_length=32),
        ),
    ]
