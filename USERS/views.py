from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .email import *
from django.core.cache import cache
from . models import *
from UI_ELEMENTS.models import *
from PRODUCTS.models import *
from django.db.models import Q
from django.views import View
import random,hashlib
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.http import Http404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from django.views.generic import ListView
from django.core.paginator import Paginator
import razorpay,requests 
from ECHOTUNES.settings import RAZORPAY_API_KEY,RAZORPAY_API_SECRET


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
    products = Product.objects.order_by('-created_at')[:8]
    brands = Brand.objects.all()
    subs = Sub_Category.objects.all()
    return render(request, 'user/user_home.html', {'banners': banners, 'products': products, 'brands': brands, 'subs': subs})
  


class UserProductDetails(View):

  def get(self, request, pk):
    variant = get_object_or_404(Product_Variant, id=pk)
    return render(request, 'user/user_product_details.html', {'variant': variant})
  

class UserProductList(ListView):

  def get(self, request):      
    brands = Brand.objects.values_list('id','name')
    subcategories = Sub_Category.objects.values_list('id','name')
    products = Product.objects.all()  
    brand_items = request.GET.getlist('brand_items')
    sub_items = request.GET.getlist('sub_items')
    discount_items = request.GET.getlist('discount')
    sort_option = request.GET.get('sort')
    min_limit = request.GET.get('min')
    max_limit = request.GET.get('max')
    search_key = request.GET.get('search')
    page_number = request.GET.get('page')

    if brand_items or discount_items or sort_option or min_limit or max_limit:
      params=True
    else:
      params=False

    if search_key:
      products = Product.objects.filter( Q(name__istartswith=search_key) | Q(brand__name__istartswith=search_key) | Q(sub_category__name__istartswith=search_key) )


    variants = []
    for product in products:
      variant = product.variants.order_by('selling_price').first()
      if variant:
        try:
          variant.is_in_wishlist = WishListItem.objects.filter(product=product,wishlist=request.user.wishlist).exists()    
        except:
          variant.is_in_wishlist = False
        finally:
          variants.append(variant)

    if brand_items and sub_items:
      variants = [variant for variant in variants if str(variant.product.sub_category.id) in sub_items and str(variant.product.brand.id) in brand_items]
    elif brand_items:
      variants = [variant for variant in variants if str(variant.product.brand.id) in brand_items]
    elif sub_items:
      variants = [variant for variant in variants if str(variant.product.sub_category.id) in sub_items]
    # else:
    #   variants = []

    variants10,variants20,variants30,variants40,variants50=[],[],[],[],[]
    if discount_items:
      if '10' in discount_items:
        variants10 = [variant for variant in variants if  10 <= variant.discount_percentage < 20 ]
      if '20' in discount_items:
        variants20 = [variant for variant in variants if  20 <= variant.discount_percentage < 30 ]
      if '30' in discount_items:
        variants30 = [variant for variant in variants if  30 <= variant.discount_percentage < 40 ]
      if '40' in discount_items:
        variants40 = [variant for variant in variants if  40 <= variant.discount_percentage < 50 ]
      if '50' in discount_items:
        variants50 = [variant for variant in variants if  50 <= variant.discount_percentage ]
      variants = variants10+variants20+variants30+variants40+variants50
        

    if min_limit and max_limit:
      if max_limit == '10000':
        variants = [variant for variant in variants if int(min_limit) < variant.selling_price]
      else:
        variants = [variant for variant in variants if int(min_limit) < variant.selling_price < int(max_limit)]

    if sort_option == 'price_low':
      variants.sort(key=lambda x: x.selling_price)
    elif sort_option == 'price_high':
      variants.sort(key=lambda x: x.selling_price, reverse=True)
    elif sort_option == 'new':
      variants.sort(key=lambda x:x.product.created_at)

    paginator = Paginator(variants, 2)
    page = paginator.get_page(page_number)

    return render(request, 'user/user_product_list.html', {'page': page, 'brands':brands,'subcategories':subcategories,'brand_items':brand_items,'sub_items':sub_items,'discount_items':discount_items,'sorted':sort_option,'params_present':params,'brand_present':bool(brand_items),'sub_present':bool(sub_items)})
  
  

class UserCart(View):

  def get(self, request):
    if request.user.is_authenticated:
      cart = Cart.objects.get_or_create(user=request.user)[0]
      if cart_items := cart.cart_items.all().order_by('id'):
        return render(request, 'user/user_cart.html',{'cart_items':cart_items,'cart':cart})
      else:
        return render(request, 'user/user_empty_cart.html')
    else:
      if cart := request.session.get('cart'):
        total_selling_price = 0 
        total_actual_price = 0
        total_discount_price = 0
        total_count = 0
        cart_items = []
        for item_data in cart.values():
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
      cart = request.session.get('cart', {})
      cart_item = cart.get(pk)
      cart_item['count'] += 1
      request.session['cart'] = cart
    return redirect(request.META.get('HTTP_REFERER'))
  

  
class SubtractCartItemCount(View):

  def get(self, request, pk):
    if request.user.is_authenticated:
      cart_item = CartItem.objects.get(product_variant_id=pk)
      cart_item.count -= 1
      cart_item.save()
    else:
      cart = request.session.get('cart', {})
      cart_item = cart.get(pk)
      cart_item['count'] -= 1
      request.session['cart'] = cart
    return redirect(request.META.get('HTTP_REFERER'))
  


class UserRemoveFromCart(View):

  def get(self, request, pk):
    if request.user.is_authenticated:
      cart_item = CartItem.objects.get(product_variant_id=pk)
      cart_item.delete()
    else:
      cart = request.session.get('cart', {})
      del cart[pk] 
      request.session['cart'] = cart
    return redirect(request.META.get('HTTP_REFERER'))
  

  
class UserProfileView(LoginRequiredMixin,View):

  def get(self, request):
    addresses = request.user.user_addresses.all()
    return render(request, 'user/user_profile.html', {'addresses':addresses})
  

  
class UserAddAddress(View):

  def post(self, request):
    address_type = request.POST.get('address_type')
    name = request.POST.get('name')
    gender = request.POST.get('gender')
    mobile = request.POST.get('mobile')
    address = request.POST.get('address')
    place = request.POST.get('place')
    landmark = request.POST.get('landmark')
    pincode = request.POST.get('pincode')
    post = request.POSt.get('post')
    district = request.POST('district')
    state = request.POST('state')
    # api_url = f"https://api.postalpincode.in/pincode/{pincode}"
    # response = requests.get(api_url)
    # if response.status_code == 200:
    #     data = response.json()
    #     postoffice = data[0]['PostOffice'][0]['Name']
    #     district = data[0]['PostOffice'][0]['District']
    #     state = data[0]['PostOffice'][0]['State']
    #     print(postoffice,district,state)
    # else:
    #     print('invalid address')
    UserAddress.objects.create(user=request.user,address_type=address_type, name=name, gender=gender, mobile=mobile,address=address, place=place, landmark=landmark, pincode=pincode, post=post, district=district, state=state)
    return redirect('user_profile')
  


class UserUpdateAddress(View):
    
  def post(self, request, pk):
    user_address = UserAddress.objects.get(id=pk)
    user_address.address_type = request.POST.get('address_type')
    user_address.name = request.POST.get('name')
    user_address.gender = request.POST.get('gender')
    user_address.mobile = request.POST.get('mobile')
    user_address.address = request.POST.get('address')
    user_address.place = request.POST.get('place')
    user_address.pincode = request.POST.get('pincode')
    user_address.landmark = request.POST.get('landmark')
    user_address.save()
    return redirect('user_profile')
  


class UserDeleteAddress(View):

  def get(self, request, pk):
    useraddress = UserAddress.objects.get(id=pk)
    useraddress.delete()
    return redirect('user_profile')



class UserWishListView(LoginRequiredMixin, View):

  def get(self, request):
    wishlist = WishList.objects.get_or_create(user=request.user)[0]
    if wishlist_items := wishlist.wishlist_items.all():
      wishlist_item_variants = []
      for wishlist_item in wishlist_items:
          variant = wishlist_item.product.variants.order_by('selling_price').first()
          if variant:
              wishlist_item_variants.append(variant) 
      return render(request, 'user/user_wishlist.html', {'wishlist_items':wishlist_item_variants})
    else:
      return render(request, 'user/user_empty_wishlist.html')



class UserUpdateWishListView(LoginRequiredMixin, View):

  def get(self, request, pk):
    wishlist = WishList.objects.get_or_create(user=request.user)[0]
    product=Product.objects.get(id=pk)
    wishlist_item,wishlist_item_created = WishListItem.objects.get_or_create(wishlist=wishlist,product=product)
    if not wishlist_item_created:
      wishlist_item.delete()
    return redirect(request.META.get('HTTP_REFERER'))


class UserCheckout(LoginRequiredMixin,View):
  def get(self, request):
    addresses = request.user.user_addresses.all()
    cart = Cart.objects.get(user=request.user)
    if cart_items := cart.cart_items.all().order_by('id'):
      return render(request, 'user/user_checkout.html', {'addresses':addresses, 'cart':cart, 'cart_items':cart_items})
    else:
      return redirect('user_cart')
  
  def post(self, request):
    address_id=request.POST.get('address')
    payment_method = request.POST.get('payment_method')
    address = UserAddress.objects.get(id=address_id)
    order = Order.objects.create(user=request.user, address=address, payment_method=payment_method)
    for item in request.user.cart.cart_items.all():
      print(item,item.product_variant)
      product_variant = item.product_variant    
      OrderItem.objects.create(order=order, product_variant=product_variant)

    if payment_method == 'online':
      client = razorpay.Client(auth=(RAZORPAY_API_KEY,RAZORPAY_API_SECRET))
      data = { "amount": request.user.cart.total_selling_price, "currency": "INR","receipt": str(order.id), }
      payment = client.order.create(data=data)
      order_id = payment["id"] 
      order.razorpay_order_id = order_id
      order.status = 'success'
      order.save()
    return redirect('user_home')