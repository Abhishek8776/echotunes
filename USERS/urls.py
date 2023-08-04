from django.urls import path
from . import views

urlpatterns = [
    path('',views.home, name='home'),
    path('signup/',views.signup_user,name='signup'),
    path('otp/' ,views.verify_otp, name='otp' ),
    path('signin/', views.signin, name='signin'),
    path('signout/',views.signout,name='signout'),
    path('details/<str:pk>/',views.product_details,name='details')
]