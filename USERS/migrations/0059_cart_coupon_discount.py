# Generated by Django 4.2.4 on 2023-09-27 03:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('USERS', '0058_order_coupon_discount_price_order_total_actual_price_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='coupon_discount',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
