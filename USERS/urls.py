from django.urls import path
from . import views

urlpatterns = [
    path('signup/',views.SignupUser.as_view(),name='signup'),
    path('verification/<str:key>/' ,views.VerifyOTP.as_view(), name='verify_otp' ),
    path('resendotp/<str:key>/',views.ResndOTP.as_view(),name='resend'),
    path('signin/', views.SignIn.as_view(), name='signin'),
    path('forgot/',views.ForgotPassword.as_view(),name='forgot'),
    path('reset_password/<str:uid>/<str:token>/', views.ResetPassword.as_view(), name='reset'),
    path('signout/',views.signout.as_view(),name='signout'),
]