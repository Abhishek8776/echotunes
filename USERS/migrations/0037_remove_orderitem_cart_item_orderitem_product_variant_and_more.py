# Generated by Django 4.2.4 on 2023-09-06 08:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('PRODUCTS', '0022_rename_discount_price_product_variant_selling_price'),
        ('USERS', '0036_alter_order_payment_method'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderitem',
            name='cart_item',
        ),
        migrations.AddField(
            model_name='orderitem',
            name='product_Variant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='PRODUCTS.product_variant'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(default='failed', max_length=30),
        ),
    ]
