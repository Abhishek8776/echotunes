from django.urls import path
from . import views

urlpatterns = [
    path('',views.home.as_view(), name='home'),
    path('signup/',views.signup_user.as_view(),name='signup'),
    path('otp/' ,views.verify_otp.as_view(), name='otp' ),
    path('signin/', views.signin.as_view(), name='signin'),
    path('signout/',views.signout.as_view(),name='signout'),
    path('details/<str:pk>/',views.product_details.as_view(),name='details')
]