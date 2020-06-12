from .models import *
from django.shortcuts import render, redirect
from .forms import *
from django.contrib import messages

def prepareForOrder(request, orderProduct_qs, product,):
    if orderProduct_qs.exists():
        orderProduct = orderProduct_qs[0]
    else:
        orderProduct = OrderedProduct.objects.create(product=product, ordered_by=request.user)
        orderProduct.save()
        orderProduct = OrderedProduct.objects.get(product=product, ordered_by=request.user)
    order_qs = Order.objects.filter(createdBy=request.user, hasPayed=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(product__id=product.id).exists():
            orderProduct.quantity += 1
            orderProduct.save()
        else:
            order.items.add(orderProduct)
    else:
        order = Order.objects.create(createdBy=request.user)
        #orderProduct.quantity = 1
        #orderProduct.save()
        order.items.add(orderProduct)
        order.save()

def getCategoryProducts():
    bd = ProductCategory.objects.get(name='Best Deals')
    cp = ProductCategory.objects.get(name='Car Parts')
    best_deals = bd.products.all()
    car_parts = cp.products.all()
    return best_deals, car_parts

def handleCartView(request):
    user = request.user
    order = Order.objects.filter(createdBy=request.user, hasPayed=False)
    if order.exists():
        sp_order = order[0]
        order_items = sp_order.items.all()
        return render(request, 'cart_view.html',
                      {'order_items': order_items, 'user': user, 'sp_order': sp_order})
    else:
        sp_order = Order.objects.create(createdBy=request.user, hasPayed=False)
        order_items = sp_order.items.all()
        return render(request, 'cart_view.html', {'order_items': order_items, 'sp_order': sp_order})
    return render(request, 'cart_view.html')

def handleOrderQuantityIncrease(request, item_id):
    ordered_prod = OrderedProduct.objects.get(id=item_id, ordered_by=request.user)
    ordered_prod.quantity += 1
    ordered_prod.save()
    return redirect('/cart_view')

def handleOrderQuantityDecrease(request, item_id):
    ordered_prod = OrderedProduct.objects.get(id=item_id, ordered_by=request.user)
    if ordered_prod.quantity == 1:
        return redirect('/cart_view')
    ordered_prod.quantity -= 1
    ordered_prod.save()
    return redirect('/cart_view')

def handleRemoveFromCart(request, item_id):
    order_qs = Order.objects.filter(createdBy=request.user, hasPayed=False)
    order = order_qs[0]
    if order.items.filter(id=item_id, ordered_by=request.user).exists():
        item = OrderedProduct.objects.get(id=item_id)
        item.delete()
        return redirect('/cart_view')
    return redirect('/cart_view')

def grabOrder(creator, pay_status):
    return Order.objects.get(createdBy=creator, hasPayed=pay_status)

def createBillingInfo(user, state, address):
    return BillingInfo(
        user=user,
        state=state,
        address=address
    )

def processStripePay(post_dict, req_user, order):
    state = post_dict.get('state')
    address =  post_dict.get('address')
    billing = createBillingInfo(req_user, state, address)
    billing.save()
    order.billing_address = billing
    order.save()
    return redirect('/payment')

def processPayOnDelivery(post_dict, order, req_user, req_obj):
    state = post_dict.get('state')
    address = post_dict.get('address')
    billing = createBillingInfo(req_user, state, address)
    billing.save()
    order.billingAddress = billing
    order.hasPayed = True
    order.save()
    messages.info(req_obj, 'Your order has been successfully placed. Item would be delivered within 12hrs.')
    order = Order.objects.create(createdBy=req_user, hasPayed=False)
    return render(req_obj, 'cart_view.html')



def handleCheckoutPost(post_dict, req_user, req_obj, err1, err2):
    form = CheckOutForm(post_dict or None)
    try:
        if form.is_valid:
            payment_option = post_dict['payment-method']
            order = grabOrder(req_user, False)
            if payment_option == 'S':
                return processStripePay(post_dict, req_user, order)
            return processPayOnDelivery(post_dict, order, req_user, req_obj)
    except err1:
        messages.info(req_obj, 'You do not have an active order')
        return redirect('/cart_view')
    except err2:
        messages.info(req_obj, 'Please choose a payment option')
        return redirect('/checkout')

def handleCheckOutGet(req_user, req_obj):
    form = CheckOutForm()
    sp_order = grabOrder(req_user, False)
    items = sp_order.items.all()
    context = {
        'form': form,
        'sp_order': sp_order,
        'items': items
    }
    if sp_order.getOrderTotalItems() == 0:
        messages.info(req_obj,
                      'You do not have any item in your cart. Add an Item to your cart before you checkout')
        return redirect('/cart_view')
    return render(req_obj, 'chekout.html', context)

def handlePaymentGetRequest(req_user, req_obj):
    sp_order = grabOrder(req_user, False)
    order_items = sp_order.items.all()
    return render(req_obj, 'payment.html', {'sp_order': sp_order, 'order_items': order_items})
