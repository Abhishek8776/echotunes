from typing import Any
from django.db import models
from base.models import BaseModel
from django.core.exceptions import ValidationError


# Create your models here.


class Brand(BaseModel):
  brand_name = models.CharField(max_length=100, unique=True)
  logo = models.ImageField(upload_to='brand/',null=True,blank=True)
  
  def __str__(self):
    return self.brand_name
  


class Category(BaseModel):
  category_name = models.CharField(max_length=100 , unique=True)

  def __str__(self):
     return self.category_name
  
  class Meta:
    verbose_name_plural = "categories"



class Sub_Category(BaseModel):
    sub_category_name = models.CharField(max_length=100 ,unique=True)
    image = models.ImageField(upload_to="subcategory/",null=True,blank=True)
    category = models.ForeignKey(Category , on_delete=models.CASCADE ,related_name='sub_categories')

    def __str__(self):
      return self.sub_category_name
    
    class Meta:
      verbose_name_plural = "sub categories"



class Product(BaseModel):
    model_name = models.CharField(max_length=100)    
    brand = models.ForeignKey(Brand , on_delete=models.CASCADE ,related_name='brands')
    category = models.ForeignKey(Category , on_delete=models.CASCADE ,related_name='categories')
    sub_category = models.ForeignKey(Sub_Category , on_delete=models.CASCADE ,related_name='sub_categories')
    image1 = models.ImageField(upload_to="product/",null=True,blank=True)
    image2 = models.ImageField(upload_to="product/",null=True,blank=True)
    image3 = models.ImageField(upload_to="product/",null=True,blank=True)
    image4 = models.ImageField(upload_to="product/",null=True,blank=True)
    actual_price = models.IntegerField()
    selling_price = models.IntegerField()
    stock = models.IntegerField()
    description =models.TextField()
    visibility = models.BooleanField(default=True)

    def __str__(self):
     return self.model_name
      
    def clean(self):
        if self.actual_price and self.selling_price and (self.actual_price < self.selling_price):
            raise ValidationError({"actual_price": "Actual price must be greater than selling price."})

# class ProductImage(BaseModel):
#     product = models.ForeignKey(Product , on_delete=models.CASCADE)
#     image = models.ImageField(upload_to="product/")