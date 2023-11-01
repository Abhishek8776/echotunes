# Generated by Django 4.2.4 on 2023-09-26 06:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PRODUCTS', '0028_rename_amount_coupon_minimum_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='coupon',
            name='count',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='discount',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='coupon',
            name='minimum_amount',
            field=models.PositiveIntegerField(default=0),
        ),
    ]