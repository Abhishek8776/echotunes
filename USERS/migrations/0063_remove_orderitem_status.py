# Generated by Django 4.2.4 on 2023-10-02 18:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('USERS', '0062_remove_order_status_orderitem_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='status',
        ),
    ]
