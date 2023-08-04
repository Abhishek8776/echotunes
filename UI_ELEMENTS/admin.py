from django.contrib import admin
from . models import *


# Register your models here.

class BannerAdmin(admin.ModelAdmin):
  list_display = ['id', 'image', 'created_at', 'updated_at']
  search_fields = ['id']
  readonly_fields = ['created_at','updated_at']


admin.site.register(Banner, BannerAdmin)
