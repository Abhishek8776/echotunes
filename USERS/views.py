from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .email import *
from django.core.cache import cache
from . models import *
from UI_ELEMENTS.models import *
from PRODUCTS.models import *
from django.views import View
import random,hashlib
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.oauth2.client import OAuth2Client


class UserSignup(View):
  
  def get(self, request):
    return render(request, 'user/user_signup.html')

  def post(self, request):
    name = request.POST.get('name')
    email = request.POST.get('email')
    password = request.POST.get('pass')
    userobj = User.objects.filter(email=email).first()
    if userobj:
      messages.warning(request, 'You are already registered, Please sign in')
      return redirect('user_signin')
    otp = str(random.randint(100000, 999999))
    account_verification_email(email, name, otp)
    key = hashlib.sha256(email.encode()).hexdigest()
    cache.set(key, {'email': email, 'name': name,'password': password, 'otp': otp}, timeout=600)
    return redirect('user_verify_otp', key=key)


class UserVerifyOTP(View):

  def get(self, request, key):
    signup_data = cache.get(key)
    if not signup_data:
        return redirect('user_signin')
    return render(request, 'user/user_verify_otp.html', {'key': key})

  def post(self, request, key):
    reciveotp = request.POST.get('otp1') + request.POST.get('otp2') + request.POST.get(
        'otp3') + request.POST.get('otp4') + request.POST.get('otp5') + request.POST.get('otp6')
    signup_data = cache.get(key)
    if not signup_data:
        messages.warning(request, 'OTP expired or invalid')
        return redirect('user_signin')
    otp = signup_data.get('otp')
    name = signup_data.get('name')
    email = signup_data.get('email')
    password = signup_data.get('password')
    print(reciveotp, otp)
    if reciveotp != otp:
        messages.warning(request, 'OTP mismatch')
        return redirect('user_verify_otp', key=key)
    user = User.objects.create_user(name=name, email=email, password=password)
    user.save()
    cache.delete(key)
    return redirect('user_signin')


class UserResndOTP(View):
  def get(self, request, key):
    signup_data = cache.get(key)
    if signup_data:
      email = signup_data.get('email')
      name = signup_data.get('name')
      otp = str(random.randint(100000, 999999))
      account_verification_email(email, name, otp)
      signup_data['otp'] = otp
      existing_timeout = signup_data.get('timeout', None)
      cache.set(key, signup_data, timeout=existing_timeout)
      return redirect('user_verify_otp', key=key)
    return redirect('user_signup')


class UserSignIn(View):

  def get(self, request):
    return render(request, 'user/user_signin.html')

  def post(self, request):
    email = request.POST.get('email')
    password = request.POST.get('pass')
    print(email, password)
    userobj = User.objects.filter(email=email).first()
    if not userobj:
      messages.warning(request, 'You are not registered, Please sign up')
      return redirect('user_signup')
    user = authenticate(request, email=email, password=password)
    print(user)
    if not user:
      messages.warning(request, 'Email password mismatch')
      return redirect('user_signin')
    login(request, user)
    request.session['usr_id'] = str(user.id)
    return redirect('user_home')


class UserForgotPassword(View):

  def get(self, request):
      return render(request, 'user/user_forgot.html')

  def post(self, request):
    email = request.POST.get('email')
    try:
      user = User.objects.get(email=email)
    except:
      messages.warning(request, 'You are not registerd, Please sign up')
      return redirect('user_signup')
    encrypt_id = urlsafe_base64_encode(str(user.pk).encode())
    reset_link = f"{request.scheme}://{request.get_host()}{reverse('user_reset', args=[encrypt_id])}"
    cache_key = f"reset_link_{encrypt_id}"
    cache.set(cache_key, {'reset_link': reset_link}, timeout=60)
    reset_password_email(email, reset_link)
    messages.success(request, 'Password reset link sent to your email.')
    return redirect('user_signin')


class UserResetPassword(View):

  def get(self, request, encrypt_id):
    cache_key = f"reset_link_{encrypt_id}"
    cache_data = cache.get(cache_key)
    if not cache_data:
        raise Http404("Reset link has expired")
    return render(request, 'user/user_reset.html')

  def post(self, request, encrypt_id):
    cache_key = f"reset_link_{encrypt_id}"
    id = str(urlsafe_base64_decode(encrypt_id), 'utf-8')
    user = User.objects.get(pk=id)
    new_password = request.POST.get('pass')
    user.set_password(new_password)
    user.save()
    cache.delete(cache_key)
    messages.success(
        request, 'Password reset successful. You can now log in with your new password.')
    return redirect('user_signin')


class UserSignout(View):

  def get(self, request):
    logout(request)
    return redirect('user_home')


class UserHome(View):

  def get(self, request):
    if session_cart := request.session.get('cart'):
      for item_data in session_cart.values():
        product_variant=Product_Variant.objects.get(id=item_data['product_variant_id'])
        cart = Cart.objects.get_or_create(user=request.user)[0]
        cart_item,cart_item_created = CartItem.objects.get_or_create(cart=cart,product_variant=product_variant)
        if not cart_item_created:
          cart_item.count += 1
          cart_item.save()
      del session_cart
    banners = Banner.objects.all()
    products = Product.objects.all()
    brands = Brand.objects.all()
    subs = Sub_Category.objects.all()
    return render(request, 'user/user_home.html', {'banners': banners, 'products': products, 'brands': brands, 'subs': subs})
  


class UserProductDetails(View):

  def get(self, request, pk):
    variant = get_object_or_404(Product_Variant, id=pk)
    return render(request, 'user/user_product_details.html', {'variant': variant})
  

class UserCart(View):

  def get(self, request):
    if request.user.is_authenticated:
      if cart_items:= request.user.cart.cart_items.all().order_by('id'):
        total_count = sum(cart_item.count for cart_item in cart_items)
        total_selling_price = sum(cart_item.total_selling_price for cart_item in cart_items)
        total_actual_price = sum(cart_item.total_actual_price for cart_item in cart_items)
        total_discount_price = total_actual_price - total_selling_price
        return render(request, 'user/user_cart.html',{'cart_items':cart_items,'total_count':total_count,'total_selling_price':total_selling_price,'total_actual_price':total_actual_price,'total_discount_price':total_discount_price})
      else:
        return render(request, 'user/user_empty_cart.html')
    else:
      if cart := request.session.get('cart'):
        total_selling_price = 0 
        total_actual_price = 0
        total_discount_price = 0
        total_count = 0
        cart_items = []
        for key,item_data in cart.items():
          print(key,item_data)
          product_variant = Product_Variant.objects.get(id=item_data['product_variant_id'])
          count = item_data['count']
          cart_item = {
            'product_variant': product_variant,
            'product_variant_id': item_data['product_variant_id'],
            'count': count,
            'total_selling_price': count * product_variant.selling_price,
            'total_actual_price': count * product_variant.actual_price,
          }
          cart_items.append(cart_item)
          total_count += cart_item['count']
          total_selling_price += cart_item['total_selling_price']
          total_actual_price += cart_item['total_actual_price']
          total_discount_price = total_actual_price - total_selling_price
        return render(request, 'user/user_cart.html',{'cart_items':cart_items,'total_count':total_count,'total_selling_price':total_selling_price,'total_actual_price':total_actual_price,'total_discount_price':total_discount_price})
      else:
        return render(request, 'user/user_empty_cart.html')



    
class UserAddToCart(View):

  def get(self, request, pk):
    if request.user.is_authenticated:
      product_variant=Product_Variant.objects.get(id=pk)
      cart = Cart.objects.get_or_create(user=request.user)[0]
      cart_item,cart_item_created = CartItem.objects.get_or_create(cart=cart,product_variant=product_variant)
      if not cart_item_created:
        cart_item.count += 1
        cart_item.save()
    else:
      cart = request.session.get('cart', {})
      if pk in cart:
          cart[pk]['count'] += 1
      else:
          cart[pk] = {'count': 1, 'product_variant_id': pk}
      print(cart)
      request.session['cart'] = cart
    return redirect('user_product_details',pk=pk)
  


class AddCartItemCount(View):

  def get(self, request, pk):
    if request.user.is_authenticated:
      cart_item = CartItem.objects.get(product_variant_id=pk)
      cart_item.count += 1
      cart_item.save()
    else:
      product_variant = Product_Variant.objects.get(id=pk)
      cart = request.session.get('cart', {})
      cart_item = cart.get(pk)
      cart_item['count'] += 1
      request.session['cart'] = cart
    return redirect('user_cart')
  
class SubtractCartItemCount(View):

  def get(self, request, pk):
    if request.user.is_authenticated:
      cart_item = CartItem.objects.get(product_variant_id=pk)
      cart_item.count -= 1
      cart_item.save()
    else:
      product_variant = Product_Variant.objects.get(id=pk)
      cart = request.session.get('cart', {})
      cart_item = cart.get(pk)
      cart_item['count'] -= 1
      request.session['cart'] = cart
    return redirect('user_cart')
  

class UserRemoveFromCart(View):

  def get(self, request, pk):
    if request.user.is_authenticated:
      cart_item = CartItem.objects.get(product_variant_id=pk)
      cart_item.delete()
    else:
      product_variant = Product_Variant.objects.get(id=pk)
      cart = request.session.get('cart', {})
      del cart[pk] 
      request.session['cart'] = cart
    return redirect('user_cart')
  

  
class UserProfileView(View):

    def get(self, request):
        return render(request, 'user/user_profile.html')