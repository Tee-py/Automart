from django.shortcuts import render, redirect
from django.utils.datastructures import MultiValueDictKeyError
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic import View
from django.contrib.auth.models import auth
from django.contrib.auth.decorators import login_required
from datetime import datetime
import asyncio
import stripe
stripe.api_key = 'sk_test_dZAu65egVsqC3PIqPMLEROtr00duFRRHL0'
from django.contrib import messages
from .models import CustomUser
from .models import *
from .forms import *
from .functions import *
# Create your views here.

class Login(View):

    def get(self, *args, **kwargs):
        user = self.request.user
        if user.is_authenticated:
            return redirect('home')
        return render(self.request, 'automartlogin.html')

    def post(self, *args, **kwargs):
        email = self.request.POST['your_name']
        pas = self.request.POST['your_pass']
        user = auth.authenticate(email=email, password=pas)
        if user is not None:
            auth.login(self.request, user)
            print('success')
            return redirect('home')
        else:
            print('failed')
            return redirect('login')

class Register(View):
    def get(self, *args, **kwargs):
        return render(self.request, 'automartreg.html')

    def post(self, *args, **kwargs):
        email = self.request.POST['email']
        pass1 = self.request.POST['pass']
        pass2 = self.request.POST['re_pass']
        if pass1==pass2:
            try:
                user = CustomUser()
                user.email = email
                user.set_password(pass1)
                user.save()
                user = auth.authenticate(email=email, password=pass1)
                auth.login(self.request, user)
                print('success')
                return redirect('login')
            except:
                print('failed')
                return redirect('register')
        else:
            print('password err')
            return redirect('register')



def home(request):
    best_deals, car_parts = getCategoryProducts()
    return render(
        request, 'home.html',
        {
            'best_deals': best_deals,
            'car_parts': car_parts,
        }
    )


@login_required()
def add_to_cart(request, prod_id):
    product = Product.objects.get(id=prod_id)
    orderProduct_qs = OrderedProduct.objects.filter(product=product, ordered_by=request.user)
    prepareForOrder(request, orderProduct_qs, product)
    return redirect('/cart_view')

@login_required()
def cart_view(request):
   #all_cat = Item_Category.objects.all()
    return handleCartView(request)

def increase_quantity(request, item_id):
    return handleOrderQuantityIncrease(request, item_id)


def reduce_quantity(request, item_id):
    return handleOrderQuantityDecrease(request, item_id)


def remove_from_cart(request, item_id):
    return handleRemoveFromCart(request, item_id)


class CheckOutView(View):
    def post(self, *args, **kwargs):
        return handleCheckoutPost(self.request.POST, self.request.user, self.request, ObjectDoesNotExist, MultiValueDictKeyError)
    def get(self, *args, **kwargs):
        return handleCheckOutGet(self.request.user, self.request)


class PaymentView(View):
    def get(self, *args, **kwargs):
        return handlePaymentGetRequest(self.request.user, self.request)

    def post(self, *args, **kwargs):
        order = grabOrder(self.request.user, False)
        token = stripe.Token.create(
            card={"number": self.request.POST['card_number'], "exp_month": self.request.POST['Expiry month'], "exp_year": self.request.POST['Expiry year'], "cvc": self.request.POST['cvc'], })

        amount =int(order.getOrderTotalPrice() * 100)
        try:
            charge = stripe.Charge.create(amount=amount, currency="usd", source=token)
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.madeBy = self.request.user
            payment.amount = order.getOrderTotalPrice()
            payment.payment_date = datetime.now()
            payment.save()
            order.hasPayed = True
            order.payment = payment
            order.save()
            messages.success(self.request, 'Your purchase was successful')
            return redirect('/cart_view')
        except stripe.error.CardError as e:
            body = e.json_body
            error = body.get('error', {})
            messages.error(self.request, f"{error.get('message')}")
            return redirect('/payment')
        except stripe.error.RateLimitError:
            messages.error(self.request, "Rate Limit Error")
            return redirect('/payment')
        except stripe.error.InvalidRequestError:
            messages.error(self.request, "Invalid Parameters")
            return redirect('/payment')
        except stripe.error.AuthenticationError:
            messages.error(self.request, "Authentication Error")
            return redirect('/payment')
        except stripe.error.APIConnectionError:
            messages.error(self.request, "Network Error")
            return redirect('/payment')
        except stripe.error.StripeError:
            messages.error(self.request, "Something went wrong. Try again Later")
            return redirect('/payment')
        except Exception:
            messages.error(self.request, "A serious error occurred. We have been contacted")
            return redirect('/payment')


def search(request):
    if request.method == 'GET':
        q = request.GET['q']
        if q == '':
            return redirect('/')
        products = Product.objects.filter(name__icontains=q)
        return render(request, 'search_res.html', {'products': products, 'q': q})

def category(request, cat_id):
    all_cat = ProductCategory.objects.all()
    category = ProductCategory.objects.get(id=cat_id)
    products = category.products.all()
    return render(request, 'category.html', {'all_cat': all_cat, 'category': category, 'products': products})

def logout(request):
    auth.logout(request)
    return redirect('/')







#def category(request):
    #pass






