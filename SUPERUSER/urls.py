from django.urls import path
from . import views

urlpatterns = [
    path('', views.AdminSignIn.as_view(), name='admin_signin'),
    path('dashboard/', views.AdminDashboard.as_view(), name='admin_dashboard'),
    path('users/', views.AdminUser.as_view(), name='admin_user'),
    path('useraccess/<str:pk>/', views.AdminUpdateUserAccess.as_view(), name='admin_user_access'),
    path('banner/', views.AdminBanner.as_view(), name='admin_banner'),
    path('brand/', views.AdminBrand.as_view(), name='admin_brand'),
    path('category/', views.AdminCategory.as_view(), name='admin_category'),
    path('subcategory/', views.AdminSubCategory.as_view(),name='admin_sub_category'),
    path('product/', views.AdminProduct.as_view(), name='admin_product'),
    path('product/<str:pk>/', views.AdminProductVariants.as_view(),name='admin_product_variants'),
    path('coupon/', views.AdminCoupons.as_view(), name='admin_coupons'),
    path('orders/', views.AdminOrder.as_view(), name='admin_orders'),
    path('order_details/<str:pk>/', views.AdminOrderDetails.as_view(), name='admin_order_details'),
    path('update_order_status/<str:action>/<str:pk>/', views.AdminUpdateOrderStatus.as_view(), name='admin_update_order_status'),
    # path('deliver_order/<str:pk>/', views.DeliverOrder.as_view(), name='admin_deliver_order'),
]
