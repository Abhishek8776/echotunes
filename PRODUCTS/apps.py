from django.apps import AppConfig
from django.core.management import call_command
from django.core.signals import request_started
import sys


# def update_coupon_status(sender, **kwargs):
#     call_command("schedule_task")


class ProductsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "PRODUCTS"

    # def ready(self):
    #     request_started.connect(update_coupon_status, sender=self)
