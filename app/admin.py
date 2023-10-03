from django.contrib import admin
from .models import  *


@admin.register(Category)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ['id','category_name']


 


@admin.register(LatestProduct)
class LatestProductModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name','description', 'price', 'product_image', 'created_at', 'unit']


@admin.register(Product)
class ProductModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'name','description', 'ingredient','price', 'product_image', 'created_at', 'unit']



@admin.register(Cart)
class CartModelAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'quantity', 'created_at']


@admin.register(Address)
class AddressModelAdmin(admin.ModelAdmin):
    list_display = ['id', 'address']

@admin.register(Ordered)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'address', 'product', 'quantity', 'order_status','payment_method', 'created_at']

@admin.register(Rating)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user','product', 'rating', 'review']

# admin.site.register(
#     [Rating])


# admin.site.register(
#     [Ordered])