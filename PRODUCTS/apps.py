from django.apps import AppConfig
from django.core.management import call_command
import sys


class ProductsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "PRODUCTS"

    def ready(self):
        if "runserver" in sys.argv:
            call_command("schedule_task")
