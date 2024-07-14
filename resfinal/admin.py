from django.contrib import admin
from .models import CustomUser, OtpToken, Category,Timing,Products
from django.contrib.auth.admin import UserAdmin
from .models import Booking
from .models import *
# Register your models here.

class CustomUserAdmin(UserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2')}
         ),
    )


class OtpTokenAdmin(admin.ModelAdmin):
    list_display = ("user", "otp_code")


admin.site.register(OtpToken, OtpTokenAdmin)
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Category)
admin.site.register(Timing)
admin.site.register(Products)
admin.site.register(Booking)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Profile)