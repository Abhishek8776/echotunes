from django.urls import path
from . import views

urlpatterns = [
    path('',views.home.as_view(), name='home'),
    path('details/<str:pk>/',views.product_details.as_view(),name='details'),
]