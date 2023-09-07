from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin
from . manager import CustomUserManager
from django.db import models
from base.models import BaseModel
from PRODUCTS.models import Product_Variant,Product
from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver
from django.db.models import Sum


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
  
class UserAddress(models.Model):
  id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_addresses')
  name = models.CharField(max_length=100)
  gender = models.CharField(max_length=10, choices=[('Mr', 'male'),('Mrs', 'female')])
  mobile = models.CharField(max_length=10)
  address_type = models.CharField(max_length=20, choices=[('house','house'),('office','office')]) 
  place = models.CharField(max_length=100) 
  address = models.CharField(max_length=200)
  landmark = models.CharField(max_length=200)
  pincode = models.CharField(max_length=6)
  post = models.CharField(max_length=50,null=True)
  district = models.CharField(max_length=50,null=True)
  state = models.CharField(max_length=50,null=True)



class Cart(models.Model):
  id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
  total_count = models.PositiveIntegerField(default=0)
  total_selling_price = models.IntegerField(default=0)
  total_actual_price = models.IntegerField(default=0) 
  total_discount_price = models.IntegerField(default=0)
 



class CartItem(models.Model):
  id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
  cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_items')
  product_variant = models.ForeignKey(Product_Variant, on_delete=models.CASCADE, related_name='cart_items')
  count = models.PositiveIntegerField(default=1)
  total_actual_price = models.IntegerField(default=0)
  total_selling_price = models.IntegerField(default=0)


@receiver(pre_save, sender=CartItem)
def calculate_cart_item_totals(sender, instance, **kwargs):
    instance.total_selling_price = instance.count * instance.product_variant.selling_price
    instance.total_actual_price = instance.count * instance.product_variant.actual_price

@receiver(post_save, sender=CartItem)
def calculate_cart_totals_post_save(sender, instance, **kwargs):
    cart = instance.cart
    cart_items = cart.cart_items.all()
    cart.total_count = cart_items.aggregate(Sum('count'))['count__sum'] or 0
    cart.total_selling_price = cart_items.aggregate(Sum('total_selling_price'))['total_selling_price__sum'] or 0
    cart.total_actual_price = cart_items.aggregate(Sum('total_actual_price'))['total_actual_price__sum'] or 0
    cart.total_discount_price = cart.total_actual_price - cart.total_selling_price
    cart.save()



class WishList(models.Model):
  id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
  user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wishlist')



class WishListItem(models.Model):
  id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
  wishlist = models.ForeignKey(WishList, on_delete=models.CASCADE, related_name='wishlist_items')
  product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlist_items')



class Order(BaseModel):
  user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
  address = models.ForeignKey(UserAddress, on_delete=models.CASCADE, related_name='orders')
  status = models.CharField(max_length=30, default='failed')
  payment_method = models.CharField(max_length=50)



class OrderItem(models.Model):
  id = models.UUIDField(primary_key=True,default=uuid.uuid4,editable=False)
  order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
  product_variant = models.ForeignKey(Product_Variant, on_delete=models.CASCADE)
