# Generated by Django 4.2.4 on 2023-08-19 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('USERS', '0023_alter_cartitem_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='total_actual_price',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='cartitem',
            name='total_discount_price',
            field=models.IntegerField(default=0),
        ),
    ]
