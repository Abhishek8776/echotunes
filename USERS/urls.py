from django.urls import path
from . import views

urlpatterns = [
    path('signup/',views.UserSignup.as_view(),name='user_signup'),
    path('verification/<str:key>/' ,views.UserVerifyOTP.as_view(), name='user_verify_otp'),
    path('resendotp/<str:key>/',views.UserResndOTP.as_view(),name='user_resend'),
    path('signin/', views.UserSignIn.as_view(), name='user_signin'),
    path('forgot/',views.UserForgotPassword.as_view(),name='user_forgot'),
    path('reset_password/<str:encrypt_id>/', views.UserResetPassword.as_view(), name='user_reset'),
    path('signout/', views.UserSignout.as_view(),name='user_signout'),

    path('', views.UserHome.as_view(), name='user_home'),
    path('product_list/', views.UserProductList.as_view(), name='product_list'),
    path('details/<str:pk>/', views.UserProductDetails.as_view(), name='user_product_details'),

    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('add_address/', views.UserAddAddress.as_view(), name='add_address'),
    path('update_address/<str:pk>', views.UserUpdateAddress.as_view(), name='update_address'),
    path('delete_address/<str:pk>', views.UserDeleteAddress.as_view(), name='delete_address'),

    path('cart/', views.UserCart.as_view(), name='user_cart'),
    path('add_cart_item/<str:pk>/', views.UserAddToCart.as_view(), name='user_add_to_cart'),
    path('add_cart_item_count/<str:pk>/', views.AddCartItemCount.as_view(), name='add_cart_item_count'),
    path('subtract_cart_item_count/<str:pk>/', views.SubtractCartItemCount.as_view(), name='subtract_cart_item_count'),
    path('remove_cart_item/<str:pk>/', views.UserRemoveFromCart.as_view(), name='remove_cart_item'),
    path('wishlist/', views.UserWishListView.as_view(), name='wish_list'),
    path('update_wishlist_items/<str:pk>/',views.UserUpdateWishListView.as_view(), name='update_wishlist_items'),

    path('checkout/',views.UserCheckout.as_view(), name='checkout'),
]