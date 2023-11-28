from typing import Any, Iterable, Optional
from django.db import models
from base.models import BaseModel
from UI_ELEMENTS.models import *
from django.core.exceptions import ValidationError
from colorfield.fields import ColorField
from django.db.models import Avg
import uuid
from datetime import date
from django.db.models.signals import *
from django.dispatch import receiver

# Create your models here.


class Brand(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    logo = models.ImageField(upload_to="brand/", null=True, blank=True)

    def __str__(self):
        return self.name


class Category(BaseModel):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "categories"


class Sub_Category(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    image = models.ImageField(upload_to="subcategory/", null=True, blank=True)
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="sub_categories"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "sub categories"


class Product(BaseModel):
    name = models.CharField(max_length=100)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="brands")
    category = models.ForeignKey(
        Category, on_delete=models.CASCADE, related_name="categories"
    )
    sub_category = models.ForeignKey(
        Sub_Category, on_delete=models.CASCADE, related_name="sub_categories"
    )
    description = models.TextField()
    visibility = models.BooleanField(default=True)

    @property
    def average_rating(self):
        return self.reviews.aggregate(Avg("rating"))["rating__avg"]

    def __str__(self):
        return self.name


class Product_Variant(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    color_name = models.CharField(max_length=100, null=True)
    color = ColorField(null=True)
    actual_price = models.IntegerField()
    selling_price = models.IntegerField()
    discount_percentage = models.IntegerField()
    stock = models.IntegerField()
    cover_image = models.ImageField(upload_to="product/", null=True, blank=True)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="variants"
    )

    def save(self, *args, **kwargs):
        actual_price = int(self.actual_price)
        selling_price = int(self.selling_price)
        self.discount_percentage = round(
            (((actual_price - selling_price) / actual_price) * 100)
        )
        super(Product_Variant, self).save(*args, **kwargs)


@receiver(pre_save, sender=Product_Variant)
def remove_out_of_stock_from_cart_items(sender, instance, **kwargs):
    if out_of_stock_items := instance.cart_items.all().filter(count=0):
        out_of_stock_items.delete()
        print("out of stock products deleted")


class ProductVarientImage(models.Model):
    id = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    image = models.ImageField(upload_to="product/", null=True, blank=True)
    product_variant = models.ForeignKey(
        Product_Variant, on_delete=models.CASCADE, related_name="variant_images"
    )


class Coupon(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True)
    details = models.CharField(max_length=200)
    count = models.PositiveIntegerField(default=0)
    discount = models.PositiveIntegerField(default=0)
    minimum_amount = models.PositiveIntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    status = models.CharField(null=True)

    def save(self, *args, **kwargs):
        if date.today() < self.start_date:
            self.status = "Upcomming"
        elif date.today() <= self.end_date:
            self.status = "Active"
        else:
            self.status = "Expired"
        super(Coupon, self).save(*args, **kwargs)

    # @property
    # def status(self):
    #   if date.today() < self.start_date:
    #     return 'Upcomming'
    #   elif date.today() <= self.end_date:
    #     return 'Active'
    #   else:
    #     return 'Expired'

    # def save(self, *args, **kwargs):
    #   if self.discount > self.minimum_amount:
    #     raise ValidationError("Discount cannot be greater than the minimum amount.")
    #   super(Coupon, self).save(*args, **kwargs)


class Banner(BaseModel):
  image = models.ImageField(upload_to="banner/")
  product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
