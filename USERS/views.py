from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .email import *
from django.core.cache import cache
from . models import *
from UI_ELEMENTS.models import *
from PRODUCTS.models import *
from django.db.models import Q,Count,Avg
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
import razorpay,json
from ECHOTUNES.settings import RAZORPAY_API_KEY,RAZORPAY_API_SECRET
from django.http import HttpResponse
from django.template.loader import get_template,render_to_string
# import pdfkit
from xhtml2pdf import pdf
# from weasyprint import HTML
from xhtml2pdf import pisa
import os
from django.core.serializers import serialize
from django.core.serializers.json import DjangoJSONEncoder
from django.core import serializers
from django.db.models import F
from django.forms.models import model_to_dict
from django.db.models.functions import Cast
from django.db.models import Value, CharField
from io import BytesIO




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
    reciveotp = request.POST.get('otp1') + request.POST.get('otp2') + request.POST.get('otp3') + request.POST.get('otp4') + request.POST.get('otp5') + request.POST.get('otp6')
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
        # cart = Cart.objects.get_or_create(user=request.user)[0]
        # cart_item,cart_item_created = CartItem.objects.get_or_create(cart=cart,product_variant=product_variant)
        cart_item,cart_item_created = CartItem.objects.get_or_create(cart=request.user.cart,product_variant=product_variant)
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
    variant.is_ordered = False
    if request.user.is_authenticated:
      variant.is_in_cart = CartItem.objects.filter(cart=request.user.cart,product_variant=variant).exists()
      for order in request.user.orders.all():
        for orderitem in order.order_items.all():
          if variant.product.id == orderitem.product_variant['product_id']:
            variant.is_ordered = True
            break
    else:
      try:
        variant.is_in_cart = bool(request.session.get('cart').get(pk))
      except:
        variant.is_in_cart = False
    rating_data = {}
    if reviews := Review.objects.filter(product=variant.product):
      for rating_value in range(5,0,-1):
        rating_count = reviews.filter(rating=rating_value).count()
        rating_percentage = rating_count/len(reviews)*100 
        rating_data[rating_value] = {'count':rating_count,'percentage':rating_percentage}
      reviews.current_user_review = reviews.filter(user=request.user).first() if request.user.is_authenticated else None
      print(variant.is_in_cart)
    return render(request, 'user/user_product_details.html', {'variant': variant, 'reviews':reviews , 'rating_data':rating_data})
  


class UserProductList(View):

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

    # if brand_items or discount_items or sort_option or min_limit or max_limit:
    #   params=True
    # else:
    #   params=False
    params = bool(brand_items or discount_items or sort_option or min_limit or max_limit)

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
      user_cart = Cart.objects.get_or_create(user=request.user)[0]
      if cart_items := user_cart.cart_items.all().order_by('id'):
        if out_of_stock_cart_item := user_cart.cart_items.filter(product_variant__stock=0):
          out_of_stock_cart_item.delete()
          return redirect('user_cart')
        return render(request, 'user/user_cart.html',{'cart_items':cart_items,'user_cart':user_cart})
      else:
        return render(request, 'user/user_empty_cart.html')
    else:
      if cart := request.session.get('cart'):
        print(cart)
        total_selling_price = 0 
        total_actual_price = 0
        total_discount_price = 0
        total_count = 0
        cart_items = []
        for key,item_data in cart.items():
          product_variant = Product_Variant.objects.get(id=key)
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
          user_cart = {'total_count':total_count,'total_selling_price':total_selling_price, 'total_actual_price':total_actual_price, 'total_discount_price':total_discount_price}
        return render(request, 'user/user_cart.html',{'cart_items':cart_items, 'user_cart':user_cart})
      else:
        return render(request, 'user/user_empty_cart.html')



class UserAddToCart(View):

  def get(self, request, pk):
    if request.user.is_authenticated:
      product_variant=Product_Variant.objects.get(id=pk)
      cart = Cart.objects.get(user=request.user)
      CartItem.objects.get_or_create(cart=cart,product_variant=product_variant)
    else:
      cart = request.session.get('cart', {})
      cart[pk] = {'count': 1, 'product_variant_id': pk}
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
  


class UserWishListView(View):

  def get(self, request):
    if request.user.is_authenticated:
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
    else:
      return render(request,'user/user_wishlist_login.html')  



class UserUpdateWishListView(LoginRequiredMixin, View):

  def get(self, request, pk):
    wishlist = WishList.objects.get_or_create(user=request.user)[0]
    product=Product.objects.get(id=pk)
    wishlist_item,wishlist_item_created = WishListItem.objects.get_or_create(wishlist=wishlist,product=product)
    if not wishlist_item_created:
      wishlist_item.delete()
    return redirect(request.META.get('HTTP_REFERER'))
  

  
class UserProfileView(LoginRequiredMixin, View):

  def get(self, request):
    return render(request, 'user/user_profile.html')
  

  
class UserManageAddress(View):

  def get(self, request):
    addresses = request.user.user_addresses.all()
    return render(request, 'user/user_manage_address.html', {'addresses':addresses})
  


class UserAddAddress(View):

  def post(self, request):
    address_type = request.POST.get('address_type')
    name = request.POST.get('name')
    gender = request.POST.get('gender')
    mobile = request.POST.get('mobile')
    email = request.POST.get('email')
    address = request.POST.get('address')
    place = request.POST.get('place')
    landmark = request.POST.get('landmark')
    pincode = request.POST.get('pincode')
    post = request.POST.get('post')
    district = request.POST.get('district')
    state = request.POST.get('state')
    UserAddress.objects.create(user=request.user,address_type=address_type, name=name, gender=gender, mobile=mobile, email=email,address=address, place=place, landmark=landmark, pincode=pincode, post=post, district=district, state=state)
    return redirect(request.META.get('HTTP_REFERER'))
  


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
    return redirect('manage_address')
  


class UserDeleteAddress(View):

  def get(self, request, pk):
    useraddress = UserAddress.objects.get(id=pk)
    useraddress.delete()
    return redirect('manage_address')
  


class UserOrderHistory(View):
  def get(self, request):
    orders = request.user.orders.all()
    # all_order_items = []
    # for order in orders:
      # for item in order.:
        # print(order.order_items)
        # item.review = request.user.reviews.filter(product=item.product_variant.product).first()
        # all_order_items.append(item)
    return render(request, 'user/user_order_history.html',{'orders':orders})
  


class UserOrderDetails(View):
  def get(self, request, pk):
    item=OrderItem.objects.get(id=pk)
    return render(request, 'user/user_order_details.html', {'item':item}) 


class UserCheckout(LoginRequiredMixin,View):
  def get(self, request, pk=None):
    cart = Cart.objects.get(user=request.user)
    cart.coupon_discount = request.session.get('coupon_discount', 0)
    if cart.total_selling_price > cart.coupon_discount:
      cart.final_price = cart.total_selling_price - cart.coupon_discount
    else:
      cart.coupon_discount = 0
      cart.final_price = cart.total_selling_price
    cart.save()
    try:
      del request.session['coupon_discount']
    except:
      pass     
    coupons = Coupon.objects.all()
    coupons = [coupon for coupon in coupons if coupon.status == 'Active']
    addresses = request.user.user_addresses.all()
    if pk:
      product_variant=Product_Variant.objects.get(id=pk)
      cart_items = [CartItem.objects.get_or_create(cart=cart, product_variant=product_variant)[0]]
    else:
      cart_items = cart.cart_items.all().order_by('id')
    if not cart_items:
        return redirect('user_cart')
    client = razorpay.Client(auth=(RAZORPAY_API_KEY,RAZORPAY_API_SECRET))
    payment_order = client.order.create(dict(amount = cart.final_price*100, currency = "INR", payment_capture = 1))
    payment_order_id = payment_order['id']
    return render(request, 'user/user_checkout.html', {'addresses':addresses, 'cart':cart, 'cart_items':cart_items,'coupons':coupons, 'payment_api_key':RAZORPAY_API_KEY,'order_id':payment_order_id})  
   
  def post(self, request, pk=None):
    cart = request.user.cart
    address_id=request.POST.get('address')
    payment_method = request.POST.get('payment_method')
    address_data = UserAddress.objects.values('name', 'gender', 'mobile', 'email', 'address_type','place', 'address', 'landmark', 'pincode', 'post','district', 'state').get(id=address_id)
    # address_data2 = UserAddress.objects.values().get(id=address_id)
    # print(address_data1)
    # print(address_data2)
    # cart_items = []
    # for item in cart.cart_items.all():
    #   item_dict = {
    #     'id':str(item.product_variant.id),
    #     'brand': item.product_variant.product.brand.name,
    #     'product_name':item.product_variant.product.name,
    #     'color':item.product_variant.color_name,
    #     'count':item.count,
    #     'selling_price':item.total_selling_price,
    #     'actual_price':item.total_actual_price,
    #   }
    #   cart_items.append(item_dict)
    # order_items = list(cart.cart_items.annotate(
    #   variant_id=Cast('product_variant__id', CharField()), brand_name = F('product_variant__product__brand__name'), product_name = F('product_variant__product__name'), color = F('product_variant__color_name')).values('variant_id','brand_name', 'product_name','color','count','count','total_selling_price','total_actual_price'))
    # print(order_items)
    # order_items = list(cart.cart_items.annotate(variant_id = F('product_variant__id'), product_name = F('product_variant__product__name'), brand = F('product_variant__product__brand__name'),color=F('product_variant__color_name')).values('count', 'total_actual_price', 'brand', 'total_selling_price','variant_id', 'product_name', 'color'))
    # for item in order_items:
    #   product_variant = Product_Variant.objects.get(id=str(item['variant_id']))
    #   product_variant.stock -= item['count']
    #   product_variant.save()
    # Order.objects.create(user=request.user, address=address_data, payment_method=payment_method, total_count=cart.total_count, total_discount_price=cart.total_discount_price, coupon_discount=cart.coupon_discount, total_actual_price=cart.total_actual_price, total_selling_price=cart.total_selling_price, final_price=cart.final_price,order_items=order_items)  
    
    

    order = Order.objects.create(user=request.user, address=address_data, payment_method=payment_method, total_count=cart.total_count, total_discount_price=cart.total_discount_price, coupon_discount=cart.coupon_discount, total_actual_price=cart.total_actual_price, total_selling_price=cart.total_selling_price, final_price=cart.final_price)    

    for item in cart.cart_items.all():
      id=str(item.product_variant.id)
      product = item.product_variant.product
      # product = model_to_dict(item.product_variant.product)
      # print(product)
      product_variant = Product_Variant.objects.values().get(id=id)
      product_variant['id'] = str(id)
      product_variant['cover_image'] = '/media/'+ product_variant['cover_image'] 
      product_variant['product_id'] = str(product.id)
      product_variant['brand'] = product.brand.name
      product_variant['product_name'] = product.name
      product_variant['product_description'] = product.description

      OrderItem.objects.create(order=order, count=item.count, total_actual_price=item.total_actual_price , total_selling_price=item.total_selling_price, product_variant=product_variant)
      print(product_variant)

    return redirect(request.META.get('HTTP_REFERER'))
    return redirect('user_home')
  


class UserReview(View):
  def post(self, request, pk):
    rating=request.POST.get('rating')
    title=request.POST.get('title')
    description = request.POST.get('description')
    images = request.FILES.getlist('images')
    product = Product.objects.get(id=pk)
    review = Review.objects.update_or_create(user=request.user,product=product,defaults={'rating': rating,'title': title,
    'description': description})[0]
    if review and images:
      for image in images:
        ReviewImage.objects.create(image=image, review=review)
    return redirect(request.META.get('HTTP_REFERER'))

class UserApplyCoupon(View):
  def get(self, request, coupon_code):
    if coupon := Coupon.objects.filter(code=coupon_code).first():
      request.session['coupon_discount'] = coupon.discount  
    return redirect(request.META.get('HTTP_REFERER'))


class UserInvoice(View):
  def get(self, request, pk):
    template_name = 'user/invoice.html'
    order = request.user.orders.get(id=pk)
    context = {'order':order}
    html_content = render_to_string(template_name, context)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoice.pdf.pdf"'
    pisa_status = pisa.CreatePDF(html_content, dest=response,encoding='utf-8')
    if pisa_status:
      return response
    return None
