# Generated by Django 4.2.4 on 2023-09-07 10:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('USERS', '0040_useraddress_district_useraddress_post_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraddress',
            name='email',
            field=models.EmailField(max_length=254, null=True),
        ),
    ]