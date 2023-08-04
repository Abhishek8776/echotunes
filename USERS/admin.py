from django.contrib import admin
from . models import *

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    exclude = ['password','is_staff','is_superuser','groups','user_permissions']
    list_display = ['id', 'name','email','is_active']  
    search_fields = ['email', 'name'] 
    readonly_fields = ['last_login','date_joined']
    
admin.site.register(User, UserAdmin)