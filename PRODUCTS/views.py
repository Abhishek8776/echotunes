from django.shortcuts import render,redirect,get_object_or_404
from django.views import View
from UI_ELEMENTS.models import *
from . models import *




class home(View):

  def get(self, request):
    banners = Banner.objects.all()
    products=Product.objects.all()
    brands = Brand.objects.all()
    subs = Sub_Category.objects.all()
    for product in products:
      discount = round((((product.actual_price - product.selling_price) / product.actual_price) * 100))
      product.discount = discount
    return render(request, 'user_home.html',{'banners':banners,'products':products ,'brands':brands ,'subs':subs,'discount':discount})


class product_details(View):

  def get(self, request, pk):
    product = get_object_or_404(Product, id=pk)
    product.discount = round((((product.actual_price - product.selling_price) / product.actual_price) * 100))
    return render(request, 'user_product_details.html', {'product':product})