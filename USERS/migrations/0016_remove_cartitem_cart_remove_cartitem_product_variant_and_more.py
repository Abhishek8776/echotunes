# Generated by Django 4.2.4 on 2023-08-17 12:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('USERS', '0015_rename_product_cartitem_product_variant'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cartitem',
            name='cart',
        ),
        migrations.RemoveField(
            model_name='cartitem',
            name='product_variant',
        ),
        migrations.DeleteModel(
            name='Cart',
        ),
        migrations.DeleteModel(
            name='CartItem',
        ),
    ]
