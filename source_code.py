# ============================== views.py ==============================

from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Car, Contact, CustomerReview, Booking
from django.db.models import Q
from urllib.parse import urlencode
from django.utils.dateparse import parse_datetime
from django.views.decorators.csrf import csrf_exempt
import razorpay

razorpay_client = razorpay.Client(
    auth=('rzp_test_r4DR8M94HImm5D', 'T4gHh7IrrXrEsPqGNT9Vc0Dm')
)

def index(request):
    return render(request, 'index.html')


def register(request):
    if request.method == "POST":
        n = request.POST['name']
        un = request.POST['username']
        num = request.POST['number']
        e = request.POST['email']
        p1 = request.POST['password']
        p2 = request.POST['password2']

        if n == '' or un == '' or num == '' or e == '' or p1 == '' or p2 == '':
            messages.error(request, "Fields can't be empty")
            return render(request, 'register.html')

        if User.objects.filter(username=un).exists():
            messages.error(request, 'Username already taken')
            return redirect('/register')

        if User.objects.filter(email=e).exists():
            messages.error(request, 'Email already taken')
            return redirect('/register')

        if p1 != p2:
            messages.error(request, 'Passwords do not match')
            return redirect('/register')

        user = User.objects.create(username=un, email=e)
        user.set_password(p1)
        user.save()
        messages.success(request, "Account created successfully")
        return redirect('/signin')

    return render(request, 'register.html')


def signin(request):
    if request.method == 'POST':
        username = request.POST['susername']
        password = request.POST['spassword']

        if username == '' or password == '':
            messages.error(request, "Fields can't be empty")
            return render(request, 'signin.html')

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, 'Logged in successfully')
            return redirect('/home')

        messages.error(request, 'Invalid credentials')
        return redirect('/signin')

    return render(request, 'signin.html')


def signout(request):
    logout(request)
    return redirect('/home')


def cars(request):
    vehicle = Car.objects.all()
    return render(request, 'cars.html', {'cars': vehicle})


def filterbyfuel(request, fid):
    vehicle = Car.objects.filter(is_active=True, fuel=fid)
    return render(request, 'cars.html', {'cars': vehicle})


def filterbytrans(request, tid):
    vehicle = Car.objects.filter(is_active=True, transmission=tid)
    return render(request, 'cars.html', {'cars': vehicle})


def filterbyseats(request, sid):
    vehicle = Car.objects.filter(is_active=True, seats=sid)
    return render(request, 'cars.html', {'cars': vehicle})


def filterbylocation(request, lid):
    vehicle = Car.objects.filter(is_active=True, loc=lid)
    return render(request, 'cars.html', {'cars': vehicle})


def sortbyprice(request, sp):
    col = 'price' if sp == '0' else '-price'
    vehicle = Car.objects.filter(is_active=True).order_by(col)
    return render(request, 'cars.html', {'cars': vehicle})


def aboutus(request):
    reviews = CustomerReview.objects.all()
    return render(request, 'aboutus.html', {'reviews': reviews})


def booking(request, cid):
    if not request.user.is_authenticated:
        return redirect('/signin')

    vehicle = Car.objects.filter(id=cid)
    return render(request, 'booking.html', {'cars': vehicle})


def contact(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        message = request.POST['message']

        if name == '' or email == '' or phone == '' or message == '':
            messages.error(request, "Fields can't be empty")
            return render(request, 'contact.html')

        Contact.objects.create(
            name=name,
            email=email,
            pnumber=phone,
            message=message
        )
        messages.success(request, "Message sent successfully")
        return redirect('/contact')

    return render(request, 'contact.html')


def review(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        rating = request.POST['rating']
        comment = request.POST['comment']
        image = request.FILES.get('image')

        if name == '' or email == '' or rating == '':
            messages.error(request, "Fields can't be empty")
            return render(request, 'reviews.html')

        CustomerReview.objects.create(
            name=name,
            email=email,
            rating=rating,
            comment=comment,
            cimage=image
        )
        messages.success(request, "Review submitted successfully")
        return redirect('/index')

    return render(request, 'reviews.html')


def carbooking(request):
    if request.method == 'POST':
        dt = request.POST['datetime']
        hr = request.POST['hours']
        car_id = request.POST['car_id']
        car_price = request.POST['car_price']

        total_rent = int(car_price) * int(hr)

        booking = Booking.objects.create(
            user=request.user,
            car_id=car_id,
            datetime=parse_datetime(dt),
            hours=int(hr),
            car_price=float(car_price),
            total_rent=total_rent
        )

        query = urlencode({'total': total_rent, 'booking_id': booking.id})
        return redirect(f'/booking/{car_id}?{query}')

    return redirect('/index')


def make_payment(request):
    booking_id = request.GET.get('booking_id')
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)

    if request.method == 'POST':
        amount = int(booking.total_rent * 100)

        razorpay_order = razorpay_client.order.create({
            'amount': amount,
            'currency': 'INR',
            'payment_capture': '1'
        })

        booking.payment_id = razorpay_order['id']
        booking.save()

        context = {
            'booking': booking,
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_merchant_key': 'rzp_test_r4DR8M94HImm5D',
            'amount': amount,
            'currency': 'INR',
            'callback_url': '/paymenthandler/'
        }
        return render(request, 'make_payment.html', context)

    return render(request, 'make_payment.html', {'booking': booking})


@csrf_exempt
def paymenthandler(request):
    if request.method == "POST":
        try:
            payment_id = request.POST.get('razorpay_payment_id')
            order_id = request.POST.get('razorpay_order_id')
            signature = request.POST.get('razorpay_signature')

            razorpay_client.utility.verify_payment_signature({
                'razorpay_order_id': order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            })

            booking = Booking.objects.get(payment_id=order_id)
            booking.payment_status = 'Paid'
            booking.save()

            return render(request, 'payment_success.html', {'booking': booking})

        except Exception as e:
            return render(request, 'payment_fail.html', {'message': str(e)})

    return redirect('/index')


def mybookings(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'MyBookings.html', {'bookings': bookings})


# ============================== models.py ==============================

from django.db import models

class Car(models.Model):
    FUEL_TYPE_CHOICES = ((1, 'Petrol'), (2, 'Diesel'), (3, 'CNG'))
    TRANS_TYPE_CHOICES = ((4, 'Manual'), (5, 'Automatic'))
    SEATS_TYPE_CHOICES = ((6, '5STR'), (7, '7STR'))
    LOCATION_CHOICES = (
        (8, 'Pune'), (9, 'Mumbai'), (10, 'Hyderabad'),
        (11, 'Chiplun'), (12, 'Ratnagiri')
    )

    carname = models.CharField(max_length=300)
    fuel = models.IntegerField(choices=FUEL_TYPE_CHOICES)
    transmission = models.IntegerField(choices=TRANS_TYPE_CHOICES)
    seats = models.IntegerField(choices=SEATS_TYPE_CHOICES)
    price = models.IntegerField(default=0)
    loc = models.IntegerField(choices=LOCATION_CHOICES)
    caraddress = models.URLField(max_length=200, default='')
    RC = models.CharField(max_length=20, default='')
    is_active = models.BooleanField(default=True)
    cimage = models.ImageField(upload_to='images')
    cimage2 = models.ImageField(upload_to='images')
    cimage3 = models.ImageField(upload_to='images')
    cimage4 = models.ImageField(upload_to='images')

    def __str__(self):
        return self.carname


class Contact(models.Model):
    name = models.CharField(max_length=30)
    email = models.EmailField()
    pnumber = models.CharField(max_length=12)
    message = models.TextField(max_length=500)

    def __str__(self):
        return self.name


class Booking(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    car_id = models.CharField(max_length=100)
    datetime = models.DateTimeField()
    hours = models.PositiveIntegerField()
    car_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_rent = models.DecimalField(max_digits=10, decimal_places=2)
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    payment_status = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        return f"Booking {self.id} - {self.user.username}"


class CustomerReview(models.Model):
    RATING_CHOICES = [(i, f"{i} Star") for i in range(1, 6)]

    name = models.CharField(max_length=100)
    cimage = models.ImageField(upload_to='images', default='')
    email = models.EmailField()
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


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
