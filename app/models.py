from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser, Group, Permission  # Import Group
from django.utils.translation import gettext as _




class Address(models.Model):
    user = models.ForeignKey(User, verbose_name="User", on_delete=models.CASCADE)
    address = models.CharField(max_length=150, verbose_name="address")

    def __str__(self):
        return self.address



class Category(models.Model):
    category_name = models.CharField(max_length=50)

    def __str__(self):
        return self.category_name


class Product(models.Model):

    Product_CHOICES=(
        ("gm","Gram"),
        ("kg","Kilogram"),
        ("pc","Piece"),
        ("packet","Packet")
        )    

    name = models.CharField(max_length=50)
    description = models.CharField(max_length=300)
    ingredient = models.CharField(max_length=300)
    category = models.ForeignKey(Category, related_name="products", on_delete=models.CASCADE, null=True)
    product_image = models.ImageField(upload_to='product', blank=True, null=True, verbose_name="Product Image")
    price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created Date")
    unit = models.CharField(max_length=100,choices=Product_CHOICES)

    def __str__(self):
        return self.name
    

class LatestProduct(models.Model):

    Product_CHOICES=(
        ("gm","Gram"),
        ("kg","Kilogram"),
        ("pc","Piece"),
        ("packet","Packet")
        )    

    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)
    category = models.ForeignKey(Category, related_name="product_category", on_delete=models.CASCADE, null=True)
    product_image = models.ImageField(upload_to='productimage', blank=True, null=True, verbose_name="Product Image")
    price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created Date")
    unit = models.CharField(max_length=100,choices=Product_CHOICES)

    def __str__(self):
        return self.name
    

class Cart(models.Model):
    user = models.ForeignKey(User, verbose_name="User", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name="Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1, verbose_name="Quantity")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created Date")

    def __str__(self):
        return str(self.user)
    
    # Creating Model Property to calculate Quantity x Price
    @property
    def total_price(self):
        return self.quantity * self.product.price


ORDER_STATUS = (
    ('Pending', 'Pending'),
    ('Accepted', 'Accepted'),
    ('Packed', 'Packed'),
    ('On The Way', 'On The Way'),
    ('Delivered', 'Delivered'),
    ('Cancelled', 'Cancelled')
)
METHOD = (
    ("Cash On Delivery", "Cash On Delivery"),
    ("Esewa", "Esewa"),
)




class Ordered(models.Model):
    user = models.ForeignKey(User, verbose_name="User", on_delete=models.CASCADE)
    product = models.ForeignKey(Product, verbose_name="Product",null=True, on_delete=models.CASCADE)
    address = models.CharField(max_length=200)
    mobile = models.IntegerField()
    email = models.EmailField(null=True, blank=True)
    quantity = models.PositiveIntegerField(verbose_name="Quantity")
    total = models.PositiveIntegerField()
    order_status = models.CharField(max_length=50,default="Pending", choices=ORDER_STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(
        max_length=20, choices=METHOD, default="Cash On Delivery")
    payment_completed = models.BooleanField(
        default=False, null=True, blank=True)

    def __str__(self):
        return "Order: " + str(self.id)


class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField()
    review = models.TextField()  # Add this field for the review

    def __str__(self):
        return str(self.user)
    
    