# Generated by Django 4.2.4 on 2023-09-11 13:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('USERS', '0049_reviewimages'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='ReviewImages',
            new_name='ReviewImage',
        ),
    ]