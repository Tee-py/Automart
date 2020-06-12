from django.contrib import admin
from .models import Product, ProductCategory, OrderedProduct, Order, BillingInfo, Payment, CustomUser

# Register your models here.
all_models = [Product, ProductCategory, OrderedProduct, Order, BillingInfo, Payment, CustomUser]

for model in all_models:
    admin.site.register(model)