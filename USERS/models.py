from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin
from . manager import CustomUserManager
from django.db import models
from base.models import BaseModel
from PRODUCTS.models import Product_Variant


import uuid


class User(AbstractBaseUser, PermissionsMixin):
  id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
  email = models.EmailField(unique=True)
  name=models.CharField(max_length=200 , null=True)
  is_active = models.BooleanField('access',default=True)
  is_staff = models.BooleanField(default=False)
  date_joined = models.DateTimeField(auto_now_add=True) 


  objects = CustomUserManager()

  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ['name']

  def __str__(self):
    return self.email
  



class Cart(models.Model):
  id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')



class CartItem(models.Model):
  id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
  cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
  product_variant = models.ForeignKey(Product_Variant, on_delete=models.CASCADE, related_name='cart_items')
  count = models.PositiveIntegerField(default=1)
  total_selling_price = models.IntegerField(default=0)
  total_actual_price = models.IntegerField(default=0)

  def save(self, *args, **kwargs):
    self.total_selling_price = self.count*self.product_variant.selling_price
    self.total_actual_price = self.count*self.product_variant.actual_price
    super(CartItem, self).save(*args, **kwargs)
