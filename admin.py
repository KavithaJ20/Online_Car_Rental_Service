# ============================== admin.py ==============================

from django.contrib import admin
from .models import Car, Contact, CustomerReview, Booking

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'carname', 'transmission', 'fuel',
        'seats', 'price', 'loc', 'is_active'
    )


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'pnumber')


@admin.register(CustomerReview)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'email', 'rating', 'created_at')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'car_id', 'datetime',
        'hours', 'total_rent', 'payment_status'
    )

