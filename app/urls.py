from django.urls import path
from .views import *
from app import views
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    
    #path('base/<int:pk>/', views.base, name='base'),



    path('recommend/', views.recommend, name='recommend'),

    path('', views.index, name='index'),
    path('reg/', views.register, name='register'),
    path('accounts/login/', views.user_login, name='login'),

    path('profile/', views.user_profile, name='profile'),

    path('changepass/', views.user_change_pass, name='change_pass'),
    path('changepass1/', views.user_change_pass1, name='change_pass1'),


    path('logout/', views.user_logout, name='logout'),

    path('caty/', views.category, name='category'),
    
    path('newproductdetail/<int:pk>/', views.newproductdetail, name='newproductdetail'),

    path('productdetail/<int:pk>/', views.productdetail, name='productdetail'),

    
    path('add-to-cart/', views.add_to_cart, name='add_to_cart'),
    #path('cart/', views.cart, name="cart"),

    path('plus-cart/<int:cart_id>/', views.plus_cart, name="plus-cart"),
    path('minus-cart/<int:cart_id>/', views.minus_cart, name="minus-cart"),
    path('remove-cart/<int:cart_id>/', views.remove_cart, name="remove-cart"),


    path('add-address/', views.AddressView.as_view(), name="add-address"),
    path('remove-address/<int:id>/', views.remove_address, name="remove-address"),
    #path('checkout/', views.checkout, name="checkout"),



    path('cartcheckout/', views.cart, name="cart"),


    path('orders/', views.orders, name="orders"),


    path("esewa-request/", EsewaRequestView.as_view(), name="esewarequest"),
    path("esewa-verify/", EsewaVerifyView.as_view(), name="esewaverify"),



    #path('eg/', views.example, name='eg'),

    path('place-esewa-order/<str:address>/<int:mobile>',placeEsewaOrder,name='place-esewa-order')


]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)