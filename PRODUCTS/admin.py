from django.contrib import admin
from . models import *

# # Register your models here.

class BrandAdmin(admin.ModelAdmin):
    list_display = ['id', 'brand_name', 'logo','created_at', 'updated_at']
    search_fields = ['id', 'brand_name']
    readonly_fields = ['created_at','updated_at']

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'category_name', 'created_at', 'updated_at']
    search_fields = ['id', 'category_name']
    readonly_fields = ['created_at','updated_at']

class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'category', 'sub_category_name', 'image' ,'created_at', 'updated_at']
    search_fields = ['id', 'sub_category_name'] 
    readonly_fields = ['created_at','updated_at']

class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'brand', 'model_name', 'category','sub_category', 'actual_price', 'selling_price', 'visibility', 'image1' , 'image2', 'image3', 'image4','created_at', 'updated_at']
    search_fields = ['id', 'brand', 'model_name'] 
    readonly_fields = ['created_at','updated_at']

  

admin.site.register(Brand, BrandAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Sub_Category, SubCategoryAdmin)
admin.site.register(Product, ProductAdmin)