import decimal
from django.shortcuts import render, HttpResponseRedirect, get_object_or_404, redirect
from .forms import*
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from .models import *
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator # for Class Based Views
from django.views import View
import requests
from django.urls import reverse

from django.contrib.auth.forms import PasswordChangeForm, SetPasswordForm
import pandas as pd
import numpy as np



def user_based_collaborative_filtering(user, num_recommendations=4):
    # Get all users except the target user
    other_users = User.objects.exclude(id=user.id)

    # Calculate user similarity using cosine similarity
    user_similarities = []
    for other_user in other_users:
        ratings_user = Rating.objects.filter(user=user)
        ratings_other_user = Rating.objects.filter(user=other_user)

        common_products = set(ratings_user.values_list('product_id', flat=True)) & set(ratings_other_user.values_list('product_id', flat=True))

        if common_products:
            user_ratings = []
            other_user_ratings = []

            for product_id in common_products:
                user_rating = ratings_user.get(product_id=product_id).rating
                other_user_rating = ratings_other_user.get(product_id=product_id).rating

                user_ratings.append(user_rating)
                other_user_ratings.append(other_user_rating)

            # Calculate cosine similarity manually
            similarity = np.dot(user_ratings, other_user_ratings) / (np.linalg.norm(user_ratings) * np.linalg.norm(other_user_ratings))
            user_similarities.append((other_user, similarity))

    # Sort similar users by similarity
    user_similarities.sort(key=lambda x: x[1], reverse=True)

    # Generate recommendations based on similar users' high-rated products
    recommended_products = set()

    for similar_user, similarity in user_similarities:
        similar_user_ratings = Rating.objects.filter(user=similar_user, rating__gte=4)

        for rating in similar_user_ratings:
            recommended_products.add(rating.product)

        if len(recommended_products) >= num_recommendations:
            break

    return list(recommended_products)[:num_recommendations]




def recommend(request):
    recommended_products = user_based_collaborative_filtering(request.user)
    print("Recommended Products:", recommended_products)  # Check if recommendations are generated

    context = {'recommended_products': recommended_products}
    return render(request, 'app/recommend.html', context)



# Create your views here.

def index(request):
    prod = LatestProduct.objects.all()
    return render(request, 'app/index.html', {'latestproduct':prod})


def category(request):
    cat = Category.objects.all()
    return render(request, 'app/category.html',  {'category':cat})



def productdetail(request, pk):
    try:
        product = Product.objects.get(id=pk)
        related_product = Product.objects.exclude(id=product.pk).filter(category=product.category)
        
        ratings = Rating.objects.filter(product=product)
        total_ratings = len(ratings)
        if total_ratings > 0:
            average_rating = sum(rating.rating for rating in ratings) / total_ratings
        else:
            average_rating = 0
        
        if request.method == 'POST' and request.user.is_authenticated:
            rating_value_str = request.POST.get('rating')
            review_text = request.POST.get('review')
            
            if rating_value_str is not None and review_text is not None:
                try:
                    rating_value = int(rating_value_str)
                    
                    # Check if the user has already rated the product
                    existing_rating = Rating.objects.filter(user=request.user, product=product).first()
                    if existing_rating:
                        existing_rating.rating = rating_value
                        existing_rating.review = review_text
                        existing_rating.save()
                        messages.success(request, 'Your rating and review have been updated!')
                    else:
                        Rating.objects.create(user=request.user, product=product, rating=rating_value, review=review_text)
                        messages.success(request, 'Thank you for your rating and review!')
                    
                    return redirect('productdetail', pk=pk)
                except ValueError:
                    messages.error(request, 'Invalid rating value. Please select a valid rating.')
            else:
                messages.error(request, 'Please provide both a rating and a review.')

        elif request.method == 'POST' and not request.user.is_authenticated:
            messages.error(request, 'You need to be logged in to submit a rating and review.')
 
        all_ratings = Rating.objects.filter(product=product)

    except Product.DoesNotExist:
        raise
           
    return render(request, 'app/productdetail.html', {
        'product': product,
        'related_product': related_product,
        'average_rating': average_rating,
        'all_ratings': all_ratings,
    })

    

# def productdetail(request, pk):
#     try:
#         #product = Product.objects.filter(id=pk).first()
#         product = Product.objects.get(id=pk)
#         #product = get_object_or_404(Product, id=pk)
#         #related_product = Product.objects.filter(category=product.category).exclude(id=pk)[:3]

#         related_product = Product.objects.exclude(id=product.pk).filter(category=product.category)
#     except Product.DoesNotExist:
#         raise
           
#     return render(request, 'app/productdetail.html',  {'product':product, 'related_product':related_product})


def newproductdetail(request, pk):
    latest = LatestProduct.objects.filter(id=pk)
    product = get_object_or_404(Product, id=pk)
    related_product = Product.objects.filter(category=product.category).exclude(id=pk)[:3]

    return render(request, 'app/newproductdetail.html',  {'product':product, 'related_product':related_product, 'lat_prod':latest})


@method_decorator(login_required, name='dispatch')
class AddressView(View):
    def get(self, request):
        form = AddressForm()
        return render(request, 'app/add_address.html', {'form': form})

    def post(self, request):
        form = AddressForm(request.POST)
        if form.is_valid():
            user=request.user
            address = form.cleaned_data['address']
            reg = Address(user=user, address=address)
            reg.save()
            messages.success(request, "New Address Added Successfully.")
        return redirect('profile')

@login_required
def remove_address(request, id):
    a = get_object_or_404(Address, user=request.user, id=id)
    a.delete()
    messages.success(request, "Address removed.")
    return redirect('profile')



@login_required
def add_to_cart(request):
    user = request.user
    product_id = request.GET.get('prod_id')
    product = get_object_or_404(Product, id=product_id)

    # Check whether the Product is alread in Cart or Not
    item_already_in_cart = Cart.objects.filter(product=product_id, user=user)
    if item_already_in_cart:
        cp = get_object_or_404(Cart, product=product_id, user=user)
        cp.quantity += 1
        cp.save()
    else:
        Cart(user=user, product=product).save()

    return redirect('cart')

@login_required
def cart(request):
    user = request.user
    cart_products = Cart.objects.filter(user=user)
    cp = [p for p in Cart.objects.all() if p.user==user]
    amount = decimal.Decimal(0)
    total_amount=0
    shipping = 100
    if cp:
        for p in cp:
            temp_amount = (p.quantity*p.product.price)
            amount += temp_amount
            
            total_amount = amount + shipping

    if request.method == 'POST':
        fm = CheckoutForm(request.POST)
        user = request.user
        if fm.is_valid():
            cart = Cart.objects.filter(user=user)
            address = fm.cleaned_data['address']
            mobile = fm.cleaned_data['mobile']
            pm = fm.cleaned_data['payment_method']
            for c in cart:
                corder = Ordered(user=c.user, product=c.product, address=address,mobile=mobile,quantity= c.quantity, total=total_amount, payment_method=pm)
                corder.save()
                if pm == 'Esewa':
                    c.delete()
                    return redirect(reverse("esewarequest") + "?o_id=" + str(corder.id))
                    
                # And Deleting from Cart
                c.delete()
            return redirect('cart')

    else:
        fm = CheckoutForm()

    context = {
        'cart_products': cart_products,
        'amount':amount,
        'total_amount':total_amount ,
        'shipping':shipping,
        'form':fm

       }

    return render(request, 'app/cart_checkout.html', context)


@login_required
def remove_cart(request, cart_id):
    if request.method == 'GET':
        c = get_object_or_404(Cart, id=cart_id)
        c.delete()
        
    return redirect('cart')


@login_required
def plus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        cp.quantity += 1
        cp.save()
    return redirect('cart')


@login_required
def minus_cart(request, cart_id):
    if request.method == 'GET':
        cp = get_object_or_404(Cart, id=cart_id)
        # Remove the Product if the quantity is already 1
        if cp.quantity == 1:
            cp.delete()
        else:
            cp.quantity -= 1
            cp.save()
    return redirect('cart')

@login_required
def checkout(request):
    user = request.user
    address_id = request.get('address')
    address = get_object_or_404(Address, id=address_id)    
    payment = request.get('payment')
    
    # Get all the products of User in Cart
    cart = Cart.objects.filter(user=user)
    for c in cart:
        # Saving all the products from Cart to Order
        Ordered(user=user, address=address, product=c.product, quantity=c.quantity,payment_method=payment).save()
        c.delete()
        if payment == 'e-Sewa':
            
            return render(request, "app/esewarequest.html" + "?o_id=" + str(Ordered.id))
     
        # And Deleting from Cart
        
    return redirect('cart')


# class EsewaRequestView(View):
#     def get(self, request, *args, **kwargs):
#         o_id = request.GET.get("o_id")
#         order = Ordered.objects.get(id=o_id)
#         context = {
#             "order": order
#         }
#         return render(request, "app/esewarequest.html", context)

import hashlib

class EsewaRequestView(View):
    def get(self, request, *args, **kwargs):
        # Retrieve the order data and other necessary information
        o_id = request.GET.get("o_id")
        order = Ordered.objects.get(id=o_id)  # Replace with your actual model and logic
        access_key = "your_access_key"  # Replace with your eSewa access key
        secret_key = "your_secret_key"  # Replace with your eSewa secret key

        # Prepare the data dictionary
        data = {
            "amount": "100",
            "tax_amount": "10",
            "total_amount": "110",
            "transaction_uuid": "ab14a8f2b02c3",
            "product_code": "EPAYTEST",
            
            "access_key": access_key,
            "signature": None, 
        }

        # Sort the data alphabetically by keys
        sorted_data = {k: data[k] for k in sorted(data)}

        # Concatenate the values into a single string
        concatenated_data = ''.join(sorted_data.values())

        # Append your eSewa API secret key
        concatenated_data_with_secret = concatenated_data + secret_key

        # Calculate the SHA-256 hash
        signature = hashlib.sha256(concatenated_data_with_secret.encode()).hexdigest()

        # Update the data dictionary with the calculated signature
        data["signature"] = signature

        context = {
            "order": order,
            "data": data,
        }
        return render(request, "app/esewarequest.html", context)
    
   


class EsewaVerifyView(View):
    def get(self, request, *args, **kwargs):
        import xml.etree.ElementTree as ET
        oid = request.GET.get("oid")
        amt = request.GET.get("amt")
        refId = request.GET.get("refId")

        url = "https://uat.esewa.com.np/epay/transrec"
        d = {
            'amt': amt,
            'scd': 'epay_payment',
            'rid': refId,
            'pid': oid,
        }
        resp = requests.post(url, d)
        root = ET.fromstring(resp.content)
        status = root[0].text.strip()

        order_id = oid.split("_")[1]
        order_obj = Ordered.objects.get(id=order_id)
        if status == "Success":
            order_obj.payment_completed = True
            order_obj.save()

            return redirect("cart")
        else:

            return redirect("/esewa-request/?o_id="+order_id)

@login_required
def orders(request):
    all_orders = Ordered.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'app/orders.html', {'orders': all_orders})


def base(request):
    return render(request, 'app/base.html')

def register(request):

    if request.method == 'POST':
        fm = CustomerRegistrationForm(request.POST)
        if fm.is_valid():
            fm.save()
            messages.success(request, 'Registration successful!')

            fm = CustomerRegistrationForm()

    else:
        fm = CustomerRegistrationForm()
    

    return render(request, 'app/register.html', {'form':fm})

def user_login(request):
    if request.method == 'POST':
        fm = AuthenticationForm(data=request.POST)
        if fm.is_valid():
            user = fm.get_user()
            login(request, user)
            return HttpResponseRedirect('/profile/')

    else:
        fm = AuthenticationForm()
    return render(request, 'app/user_login.html',{'form':fm})




def user_profile(request):
    if request.user.is_authenticated:
        #address = Address.objects.all()
        #address = Address.objects.filter(user=request.user)
        if request.method == 'POST':
            fm = EditUserProfileForm(request.POST, instance=request.user)
            if fm.is_valid():
                messages.success(request, 'Profile Updated !!')
                fm.save()
        else:
            fm = EditUserProfileForm( instance=request.user)
        return render(request, 'app/profile.html', {'name': request.user, 'fm':fm})
    else:
        return HttpResponseRedirect('/login/')


#Change Password with old password
def user_change_pass(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            fm = PasswordChangeForm(user=request.user, data=request.POST)
            if fm.is_valid():
                fm.save()
                update_session_auth_hash(request, fm.user)
                messages.success(request, 'Password change sucessfully !!')
                return redirect('profile')
        else:
            fm = PasswordChangeForm(user=request.user)
        return render(request, 'app/change_password.html', {'fm':fm})
    else:
        return HttpResponseRedirect('/accounts/login/')


#Change Password without old password
def user_change_pass1(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            fm = SetPasswordForm(user=request.user, data=request.POST)
            if fm.is_valid():
                fm.save()
                update_session_auth_hash(request, fm.user)
                messages.success(request, 'Password change sucessfully !!')
                return redirect('profile')
        else:
            fm = SetPasswordForm(user=request.user)
        return render(request, 'app/change_password.html', {'fm':fm})
    else:
        return HttpResponseRedirect('/accounts/login/')


def user_logout(request):
    logout (request)
    return HttpResponseRedirect('/accounts/login/')
