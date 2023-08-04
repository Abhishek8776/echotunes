from django.contrib.auth import login, authenticate,logout
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from .email import send_otp_email
from django.core.cache import cache
from . models import *
from UI_ELEMENTS.models import *
from PRODUCTS.models import *


# Create your views here.

def signup_user(request):

  if request.method == 'POST':
    name = request.POST.get('name')
    email = request.POST.get('email')
    password = request.POST.get('pass')
    userobj = User.objects.filter(email=email)
    if userobj.exists():
      messages.warning(request , 'You are already registerd, Please sign in')
      return redirect(signup_user)
    send_otp_email(email, name, password)
    return redirect(verify_otp)
  return render(request , 'user_signup.html')


def verify_otp(request):
  if request.method == 'POST':
    reciveotp = request.POST.get('otp1') + request.POST.get('otp2') + request.POST.get('otp3') + request.POST.get('otp4') + request.POST.get('otp5') + request.POST.get('otp6')
    try:
      name = cache.get('signup_data')['name']
      email = cache.get('signup_data')['email']
      password = cache.get('signup_data')['password']
      otp = cache.get('signup_data')['otp']
    except:
      messages.warning(request,'otp exipred')
      return redirect(verify_otp)
    print(otp,reciveotp)
    if reciveotp != otp:
      messages.warning(request , 'OTP mismatch')
      return redirect(verify_otp)
    User.objects.create_user(name = name , email = email , password=password)
    cache.delete('signup_data')
    return redirect(signin)
  return render(request , 'user_verify_otp.html')

def signin(request):

  if request.method == 'POST':
    email = request.POST.get('email')
    password = request.POST.get('pass')
    print(email,password)
    user = authenticate(request, email=email,password=password)
    print(user)
    if user is not None:
      login(request, user)
      request.session['usr_id'] = user.id
      return redirect(home)
    messages.warning(request , 'Email password mismatch')
    return redirect(verify_otp)
  return render( request , 'user_signin.html')

# def forgot(request):
#   if request.method == 'POST':
#     email = request.POST.get('email')
#     password = request.POST.get('pass')
#     userobj = User.objects.get(email=email)
#     if not userobj:
#       messages.warning(request , 'You are not registerd, Please sign up')
#       return redirect(forgot)
#     send_otp_email(email, userobj.name, password)
#     return redirect(verify_otp,newpass=password)
#   return render( request , 'forgot.html')


def signout(request):
  logout(request)
  return redirect(signin)



def home(request):
  banners = Banner.objects.all()
  products=Product.objects.all()
  brands = Brand.objects.all()
  subs = Sub_Category.objects.all()
  for product in products:
    discount = round((((product.actual_price - product.selling_price) / product.actual_price) * 100))
    product.discount = discount
  return render(request, 'user_home.html',{'banners':banners,'products':products ,'brands':brands ,'subs':subs,'discount':discount})



def product_details(request, pk):
    product = get_object_or_404(Product, id=pk)
    product.discount = round((((product.actual_price - product.selling_price) / product.actual_price) * 100))
    return render(request, 'user_product_details.html', {'product':product})