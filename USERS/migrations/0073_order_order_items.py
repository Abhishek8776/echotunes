# Generated by Django 4.2.4 on 2023-10-07 11:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('USERS', '0072_order_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='order_items',
            field=models.JSONField(null=True),
        ),
    ]
