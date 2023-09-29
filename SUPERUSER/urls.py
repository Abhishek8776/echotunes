from django.urls import path
from . import views

urlpatterns = [
    path('', views.AdminSignIn.as_view(), name='admin_signin'),
    path('dashboard/', views.AdminDashboard.as_view(), name='admin_dashboard'),
    path('banner/', views.AdminBanner.as_view(), name='admin_banner'),
    path('brand/', views.AdminBrand.as_view(), name='admin_brand'),
    path('category/', views.AdminCategory.as_view(), name='admin_category'),
    path('subcategory/', views.AdminSubCategory.as_view(),name='admin_sub_category'),
    path('product/', views.AdminProduct.as_view(), name='admin_product'),
    path('product/<str:pk>/', views.AdminProductVariants.as_view(),name='admin_product_variants'),
    path('coupon/', views.AdminCoupons.as_view(), name='admin_coupons')
]
