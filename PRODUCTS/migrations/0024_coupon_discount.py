# Generated by Django 4.2.4 on 2023-09-14 04:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PRODUCTS', '0023_coupon'),
    ]

    operations = [
        migrations.AddField(
            model_name='coupon',
            name='discount',
            field=models.IntegerField(default=0),
        ),
    ]
