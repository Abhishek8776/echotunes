# Generated by Django 4.2.4 on 2023-09-26 03:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('PRODUCTS', '0027_coupon_amount'),
    ]

    operations = [
        migrations.RenameField(
            model_name='coupon',
            old_name='amount',
            new_name='minimum_amount',
        ),
    ]