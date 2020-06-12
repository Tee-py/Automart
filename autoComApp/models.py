from django.db import models
#from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager
from django.utils.translation import ugettext_lazy as _

# Create your models here.
class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

class ProductCategory(models.Model):
    name = models.CharField(max_length=200)
    products = models.ManyToManyField('Product', null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Product Categories'

class Product(models.Model):
    name = models.CharField(max_length=200)
    #description = models.TextField()
    price = models.FloatField()
    img = models.ImageField(upload_to='product images', null=True)
    #category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class OrderedProduct(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)


    def __str__(self):
        return self.product.name

    def getOrderedProductTotalPrice(self):
        total_price = self.product.price*self.quantity
        return total_price



class Order(models.Model):
    createdBy = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    items = models.ManyToManyField(OrderedProduct)
    createdAt = models.DateTimeField(auto_now_add=True)
    hasPayed = models.BooleanField(default=False)
    payDate = models.DateTimeField(null=True)
    billingAddress = models.ForeignKey('BillingInfo', on_delete=models.SET_NULL, null=True)
    paymentInfo = models.OneToOneField('Payment', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.createdBy.email

    def getOrderTotalPrice(self):
        total_price = 0
        for orderedProduct in self.items.all():
            total_price += orderedProduct.getOrderedProductTotalPrice()
        return total_price

    def getOrderTotalItems(self):
        return len(self.items.all())



class BillingInfo(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    state = models.CharField(max_length=200)
    address = models.TextField(null=True)

    def __str__(self):
        return self.user.email

class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=100)
    madeBy = models.ForeignKey(CustomUser, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.FloatField()
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.madeBy.email