# Generated by Django 4.2.4 on 2023-09-10 07:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('USERS', '0047_remove_review_product_remove_review_user_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='review',
            name='order_item',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='review', to='USERS.orderitem'),
        ),
    ]
