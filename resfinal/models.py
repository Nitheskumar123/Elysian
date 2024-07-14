from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.conf import settings
import secrets
import datetime
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
import os

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = ("email")
    REQUIRED_FIELDS = ["username"]
    
    def _str__(self):
        return self.email
    

class OtpToken(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="otps")
    otp_code = models.CharField(max_length=6, default=secrets.token_hex(3))
    tp_created_at = models.DateTimeField(auto_now_add=True)
    otp_expires_at = models.DateTimeField(blank=True, null=True)
    
    
    def __str__(self):
        return self.user.username
    
def getFileName(request, filename):
    now_time = datetime.datetime.now().strftime("%Y%m%d%H:%M:%S")
    new_filename = "%s%s" % (now_time, filename)
    return os.path.join('uploads/', new_filename)
class Category(models.Model):
    name = models.CharField(max_length=150, null=False, blank=False)
    image = models.ImageField(upload_to=getFileName, null=False, blank=False)
    description = models.TextField(max_length=1000, null=False, blank=False)
    status = models.BooleanField(default=False, help_text="0-show 1-hidden")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Timing(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    name = models.CharField(max_length=150, null=False, blank=False)
    image = models.ImageField(upload_to=getFileName, null=False, blank=False)
    description = models.TextField(max_length=1000, null=False, blank=False)
    status = models.BooleanField(default=False, help_text="0-show 1-hidden")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Products(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    timing = models.ForeignKey(Timing, on_delete=models.CASCADE)
    name = models.CharField(max_length=150, null=False, blank=False)
    product_image = models.ImageField(upload_to=getFileName, null=False, blank=False)
    quantity = models.IntegerField(null=False, blank=False)
    original_price = models.FloatField(null=False, blank=False)
    selling_price = models.FloatField(null=False, blank=False)
    description = models.TextField(max_length=1000, null=False, blank=False)
    status = models.BooleanField(default=False, help_text="0-show 1-hidden")
    special = models.BooleanField(default=False, help_text="0-show 1-hidden")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


from django.conf import settings

class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    username = models.CharField(max_length=100)
    total_members = models.IntegerField()
    date_time = models.DateTimeField()
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} - {self.date_time}"



class Cart(models.Model):
    user=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    product=models.ForeignKey(Products,on_delete=models.CASCADE)
    product_qty=models.IntegerField(null=False,blank=False)
    created_at=models.DateTimeField(auto_now_add=True)
    @property
    def total(self):
        return self.product_qty * self.product.selling_price


class Order(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fname = models.CharField(max_length=200, null=False)
    lname = models.CharField(max_length=200, null=False)
    email = models.CharField(max_length=200, null=False)
    phone = models.CharField(max_length=200, null=False)
    address = models.TextField(null=False)
    city = models.CharField(max_length=200, null=False)
    state = models.CharField(max_length=200, null=False)
    country = models.CharField(max_length=200, null=False)
    pincode = models.CharField(max_length=200, null=False)
    total_price = models.FloatField(null=False)
    payment_mode = models.CharField(max_length=200, null=False)
    payment_id = models.CharField(max_length=200, null=True)
    orderstatus=(
        ('Pending','Pending'),
        ('Out for shipping','Out for shipping'),
        ('Completed','Completed')
    )
    status = models.CharField(max_length=200, choices=orderstatus, default='Pending')
    message = models.TextField(null=True)
    tracking_no = models.CharField(max_length=200, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return '{} - {}'.format(self.id, self.tracking_no)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    price = models.FloatField(null=False)
    quantity = models.IntegerField(null=False)

    def __str__(self):
        return '{} {}'.format(self.order.id, self.order.tracking_no)


class Profile(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    phone=models.CharField(max_length=500,null=False)
    address = models.TextField(null=False)
    city=models.CharField(max_length=500,null=False)
    state=models.CharField(max_length=500,null=False)
    country=models.CharField(max_length=500,null=False)
    pincode=models.CharField(max_length=500,null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username
    

