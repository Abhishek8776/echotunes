# Generated by Django 4.2.4 on 2023-08-18 14:09

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('USERS', '0021_rename_product_cartitem_product_variant'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cartitem',
            name='count',
            field=models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)]),
        ),
    ]
