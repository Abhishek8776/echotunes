# Generated by Django 4.2.4 on 2023-11-16 07:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('USERS', '0075_orderitem'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderitem',
            name='status',
            field=models.CharField(default='Placed', max_length=30),
        ),
    ]
