from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render,redirect,get_object_or_404
from django.contrib import messages
from .email import *
from django.core.cache import cache
from . models import *
from django.views import View
import random,hashlib
from django.contrib.auth.tokens import default_token_generator
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode


class SignupUser(View):
  def get(self, request):
    return render(request, 'user_signup.html')

  def post(self, request):
    name = request.POST.get('name')
    email = request.POST.get('email')
    password = request.POST.get('pass')
    userobj = User.objects.filter(email=email).first()
    if userobj:
      messages.warning(request, 'You are already registered, Please sign in')
      return redirect('signin')
    otp = str(random.randint(100000, 999999))
    account_verification_email(email, name, otp)
    key = hashlib.sha256(email.encode()).hexdigest()
    cache.set(key, {'email': email, 'name': name, 'password': password, 'otp': otp}, timeout=600)
    return redirect('verify_otp', key=key)


class VerifyOTP(View):
  def get(self, request, key):
    return render(request, 'user_verify_otp.html', {'key': key})

  def post(self, request, key):
    reciveotp = request.POST.get('otp1') + request.POST.get('otp2') + request.POST.get('otp3') + request.POST.get('otp4') + request.POST.get('otp5') + request.POST.get('otp6')
    signup_data = cache.get(key)
    if not signup_data:
      messages.warning(request, 'OTP expired or invalid')
      return redirect('verify_otp', key=key)
    otp = signup_data.get('otp')
    name = signup_data.get('name')
    email = signup_data.get('email')
    password = signup_data.get('password')
    print(reciveotp,otp)
    if reciveotp != otp:
      messages.warning(request, 'OTP mismatch')
      return redirect('verify_otp', key=key)
    user = User.objects.create_user(name=name, email=email, password=password)
    user.save()
    cache.delete(key)
    return redirect('signin')
  

class ResndOTP(View):
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
      return redirect('verify_otp', key=key)
    return redirect('signup')


class SignIn(View):

  def get(self, request):
    return render(request, 'user_signin.html')
  
  def post(self, request):
    email = request.POST.get('email')
    password = request.POST.get('pass')
    print(email,password)
    userobj = User.objects.filter(email=email).first()
    if not userobj:
      messages.warning(request, 'You are not registered, Please sign up')
      return redirect('signup')
    user = authenticate(request, email=email,password=password)
    print(user)
    if not user:
      messages.warning(request , 'Email password mismatch')
      return redirect('signin')
    login(request, user)
    request.session['usr_id'] = str(user.id)
    return redirect('home')
  
  
class ForgotPassword(View):

  def get(self, request):
    return render(request, 'user_forgot.html')
  
  def post(self, request):
    email=request.POST.get('email')
    try:
      user = User.objects.get(email=email)
    except:
      messages.warning(request , 'You are not registerd, Please sign up')
      return redirect('signup')
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(str(user.pk).encode())
    reset_link = f"{request.scheme}://{request.get_host()}{reverse('reset', args=[uid, token])}"
    reset_password_email(email, reset_link)
    return redirect('forgot')
  

class ResetPassword(View):
  
  template_name = 'user_reset.html'

  def get(self, request, uid, token):
    # try:
    #   uid = str(urlsafe_base64_decode(uid), 'utf-8')
    #   user = User.objects.get(pk=uid)
    # except:
    #   user = None
    # if user is not None and default_token_generator.check_token(user, token):
    #   return render(request, self.template_name)
    # else:
    return render(request, self.template_name)

  def post(self, request, uid, token):
    try:
      uid = str(urlsafe_base64_decode(uid), 'utf-8')
      user = User.objects.get(pk=uid)
    except:
      user = None
    if user is not None and default_token_generator.check_token(user, token):
      new_password = request.POST.get('pass')
      user.set_password(new_password)
      user.save()
      return redirect('signin')
    else:
      return render(request, self.template_name)


class signout(View):

  def get(self, request):
    logout(request)
    return redirect('home')