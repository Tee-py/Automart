

from django.urls import path
from . import views

urlpatterns = [
    path('payment', views.PaymentView.as_view(), name="payment"),
    path('remove_from_cart/<int:item_id>', views.remove_from_cart, name="remove_from_cart"),
    path('reduce_quantity/<int:item_id>', views.reduce_quantity, name="reduce_quantity"),
    path('increase_quantity/<int:item_id>', views.increase_quantity, name="increase_quantity"),
    path('add_to_cart/<int:prod_id>', views.add_to_cart, name='add_to_cart'),
    path('category/<int:cat_id>', views.category, name='category'),
    path('logout', views.logout, name='logout'),
    path('', views.home, name='home'),
    path('checkout', views.CheckOutView.as_view(), name="checkout"),
    path('search', views.search, name='search'),
    path('cart_view', views.cart_view, name='cart_view'),
    path('accounts/login/', views.Login.as_view(), name='login'),
    path('register', views.Register.as_view(), name='register')
]