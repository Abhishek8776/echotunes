from django.shortcuts import render,redirect,get_object_or_404
from django.views import View
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.cache import cache
from USERS.models import *
from UI_ELEMENTS.models import *
from PRODUCTS.models import *
from django.urls import reverse
from USERS.email import *
from django.http import Http404
from datetime import date




# Create your views here.
class AdminSignIn(View):

  def get(self, request):
    return render(request, 'superuser/admin_signin.html')
  
  def post(self, request):
    email = request.POST.get('email')
    password = request.POST.get('pass')
    print(email,password)
    superuserobj = User.objects.filter(email=email, is_superuser=True).first()
    if not superuserobj:
      messages.warning(request, 'Account not fount')
      return redirect('admin_signin')
    superuser = authenticate(request, email=email,password=password)
    print(superuser)
    if not superuser:
      messages.warning(request , 'Email password mismatch')
      return redirect('admin_signin')
    
    login(request, superuser)
    request.session['usr_id'] = str(superuser.id)
    return redirect('admin_dashboard')

  

  

# class AdminForgotPassword(View):

#   def get(self, request):
#     return render(request, 'user/user_forgot.html')
  
#   def post(self, request):
#     email=request.POST.get('email')
#     try:
#       user = User.objects.get(email=email,is_superuser=True)
#     except:
#       messages.warning(request , 'Account not found')
#       return redirect('user_signup')
#     encrypt_id = urlsafe_base64_encode(str(user.pk).encode())
#     reset_link = f"{request.scheme}://{request.get_host()}{reverse('reset', args=[encrypt_id])}"
#     cache_key = f"reset_link_{encrypt_id}"
#     cache.set(cache_key, {'reset_link':reset_link}, timeout=60) 
#     reset_password_email(email, reset_link)
#     messages.success(request, 'Password reset link sent to your email.')
#     return redirect('user_signin')

# class AdminResetPassword(View):
  
#   def get(self, request, encrypt_id):
#     cache_key = f"reset_link_{encrypt_id}"
#     cache_data = cache.get(cache_key)
#     if not cache_data:
#       raise Http404("Reset link has expired")
#     reset_id = cache_data.get('reset_link')
#     return render(request, 'user/user_reset.html',{'reset':reset_id})

#   def post(self, request, encrypt_id):
#     cache_key = f"reset_link_{encrypt_id}"
#     id = str(urlsafe_base64_decode(encrypt_id), 'utf-8')
#     user = User.objects.get(pk=id)
#     new_password = request.POST.get('pass')
#     user.set_password(new_password)
#     user.save()
#     cache.delete(cache_key)
#     messages.success(request, 'Password reset successful. You can now log in with your new password.')
#     return redirect('user_signin')
# class home1(View):

#   def get(self, request):
#     return render(request, 'superuser/admin_signin.html')
  
# class Product(View):

#   def get(self, request):
#     return render(request, 'superuser/admin_product.html')



class AdminDashboard(View):

  def get(self, request):
    return render(request, 'superuser/admin_dashboard.html')
  


class AdminBanner(View):

  def get(self, request):
    banners = Banner.objects.all()
    return render(request, 'superuser/admin_banner.html',{'banners':banners})
  
  def post(self,request):
    img = request.FILES.get('bannerimg')
    print(img)
    Banner.objects.create(image=img)
    return redirect('admin_banner')
  

  
class AdminBrand(View):
  def get(self, request):
    brands = Brand.objects.all()
    return render(request, 'superuser/admin_brand.html',{'brands':brands})

  def post(self, request):
    brand = request.POST.get('brand')
    logo = request.FILES.get('logo')
    Brand.objects.create(name=brand,logo=logo)
    return redirect('admin_brand')



class AdminCategory(View):
  def get(self, request):
    categories = Category.objects.all()
    return render(request, 'superuser/admin_category.html',{'categories':categories})

  def post(self, request):
    category = request.POST.get('category')
    Category.objects.create(name=category)
    return redirect('admin_category')
  

  
class AdminSubCategory(View):
  def get(self, request):
    categories = Category.objects.all()
    subcategories = Sub_Category.objects.all()
    return render(request, 'superuser/admin_sub_category.html',{'categories':categories,'subcategories':subcategories})
  
  def post(self, request):
    sub_category_name = request.POST.get('name')
    image = request.FILES.get('img')
    category_id = request.POST.get('category')
    category = Category.objects.get(id=category_id)
    Sub_Category.objects.create(name=sub_category_name,image=image,category=category)
    return redirect('admin_sub_category')
  

  
class AdminProduct(View):
  def get(self, request):
    brands = Brand.objects.all()
    subcategories = Sub_Category.objects.all()
    products = Product.objects.all()
    return render(request, 'superuser/admin_product.html',{'brands':brands,'subcategories':subcategories, 'products':products})

  def post(self, request):
    product_name = request.POST.get('name')
    subcategory_id = request.POST.get('subcategory')
    description = request.POST.get('description')
    brand_id = request.POST.get('brand')
    visibility = request.POST.get('visibility')
    print(product_name,subcategory_id,description,brand_id)
    brand = Brand.objects.get(id=brand_id)
    sub_category = Sub_Category.objects.get(pk=subcategory_id)
    category_id = sub_category.category_id
    category = Category.objects.get(id=category_id)
    Product.objects.create(name=product_name, category=category, sub_category=sub_category, brand=brand, description=description, visibility=visibility)
    return redirect('admin_product')
  

  
class AdminProductVariants(View):
  def get(self, request, pk):
    specified_product = get_object_or_404(Product, id=pk)
    variants = specified_product.variants.prefetch_related('variant_images')
    return render(request, 'superuser/admin_product_variant.html', {'product':specified_product,'variants':variants})
  
  def post(self, request, pk):
    color_name = request.POST.get('name')
    color_code = request.POST.get('code')
    actual_price = request.POST.get('actual_price')
    selling_price = request.POST.get('selling_price')
    stock = request.POST.get('stock')
    cover_image = request.FILES.get('cover')
    images = request.FILES.getlist('images')
    product = get_object_or_404(Product, id=pk)
    print(actual_price,selling_price,color_code,color_name)
    product_variant = Product_Variant.objects.create(color_name=color_name,color=color_code,actual_price=actual_price,       selling_price=selling_price,stock=stock,cover_image=cover_image,product=product)
    for image in images:
      ProductVarientImage.objects.create(image=image,product_variant=product_variant)
    return redirect('admin_product_variants',pk=pk)
  


class AdminCoupons(View):
  def get(self, request):
    current_date = date.today().strftime('%Y-%m-%d')
    coupons = Coupon.objects.all()
    return render(request, 'superuser/admin_coupon.html', {'coupons':coupons, 'current_date':current_date})
  
  def post(self, request):
    code = request.POST.get('code')
    count = request.POST.get('count')
    discount = request.POST.get('discount')
    minimum_amount = request.POST.get('minimum_amount')
    start_date = request.POST.get('start_date')
    end_date = request.POST.get('end_date')
    Coupon.objects.create(code=code, count=count, discount=discount, minimum_amount=minimum_amount,start_date=start_date, end_date=end_date)
    return redirect('admin_coupons')
    # error_message = None
    # try:
    #   Coupon.objects.create(code=code, count=count, discount=discount, minimum_amount=minimum_amount,start_date=start_date, end_date=end_date)
    # except ValidationError as e:
    #   error_message = str(e)
    # return redirect(reverse('admin_coupons') + f'?error_message={error_message}')