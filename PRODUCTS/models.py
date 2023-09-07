from typing import Any, Iterable, Optional
from django.db import models
from base.models import BaseModel
from UI_ELEMENTS.models import *
from django.core.exceptions import ValidationError
from colorfield.fields import ColorField
import uuid


# Create your models here.

class Banner(BaseModel):
  image = models.ImageField(upload_to='banner/')


class Brand(BaseModel):
  name = models.CharField(max_length=100, unique=True)
  logo = models.ImageField(upload_to='brand/',null=True,blank=True)
  
  def __str__(self):
    return self.name
  


class Category(BaseModel):
  name = models.CharField(max_length=100 , unique=True)

  def __str__(self):
     return self.name
  
  class Meta:
    verbose_name_plural = "categories"



class Sub_Category(BaseModel):
    name = models.CharField(max_length=100 ,unique=True)
    image = models.ImageField(upload_to="subcategory/",null=True,blank=True)
    category = models.ForeignKey(Category , on_delete=models.CASCADE ,related_name='sub_categories')

    def __str__(self):
      return self.name
    
    class Meta:
      verbose_name_plural = "sub categories"
    


class Product(BaseModel):
  name = models.CharField(max_length=100)    
  brand = models.ForeignKey(Brand , on_delete=models.CASCADE ,related_name='brands')
  category = models.ForeignKey(Category , on_delete=models.CASCADE ,related_name='categories')
  sub_category = models.ForeignKey(Sub_Category , on_delete=models.CASCADE ,related_name='sub_categories')
  description =models.TextField()
  visibility = models.BooleanField(default=True)

  def __str__(self):
    return self.name
  

  
class Product_Variant(models.Model):
  id = models.UUIDField(primary_key=True,editable=False,default=uuid.uuid4)
  color_name = models.CharField(max_length=100,null=True)
  color = ColorField(null=True)
  actual_price = models.IntegerField()
  selling_price = models.IntegerField()
  discount_percentage = models.IntegerField()
  stock = models.IntegerField()
  cover_image = models.ImageField(upload_to='product/',null=True,blank=True)
  product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')

  def save(self, *args, **kwargs):
    actual_price=int(self.actual_price)
    selling_price=int(self.selling_price)
    self.discount_percentage = round((((actual_price - selling_price) / actual_price) * 100))
    super(Product_Variant, self).save(*args, **kwargs)

    

class ProductVarientImage(models.Model):
  id = models.UUIDField(primary_key=True,editable=False,default=uuid.uuid4)
  image = models.ImageField(upload_to='product/',null=True,blank=True)
  product_variant = models.ForeignKey(Product_Variant, on_delete=models.CASCADE ,related_name='variant_images')
