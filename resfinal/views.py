from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
import json
from django.contrib.auth.models import User
import random
from .models import Category,Timing,Products,Cart
from .forms import RegisterForm
from .models import OtpToken
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.mail import send_mail
from django.contrib.auth import authenticate, login, logout
from .forms import UpdateProfileForm
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from email.mime.image import MIMEImage
from django.contrib.auth.decorators import login_required
from .models import Booking
from .forms import BookingForm
from reportlab.pdfgen import canvas

def index(request):
    return render(request, "index.html")

def signup(request):
    form = RegisterForm()
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! An OTP was sent to your Email")
            return redirect("verify-email", username=request.POST['username'])
    context = {"form": form}
    return render(request, "signup.html", context)


def verify_email(request, username):
    user = get_user_model().objects.get(username=username)
    user_otp = OtpToken.objects.filter(user=user).last()

    if not user_otp:
        messages.warning(request, "No OTP found for this user.")
        return redirect("verify-email", username=username)

    if request.method == 'POST':
        otp_code = request.POST.get('otp_code', '')
        if user_otp.otp_code == otp_code:
            if user_otp.otp_expires_at > timezone.now():
                user.is_active = True
                user.save()
                messages.success(request, "Account activated successfully!! You can Login.")
                
                subject = "WELCOME MAIL"
                message = f"Hi {user.username}, Welcome to our website"
                sender = "nithes262004@gmail.com"
                receiver = [user.email]
                html_content = render_to_string('new-email.html', {'username': user.username})
                msg = EmailMultiAlternatives(subject, message, sender, receiver)
                msg.attach_alternative(html_content, "text/html")
                

                msg.send(fail_silently=False)
                
                '''send_mail(
                    subject,
                    message,
                    sender,
                    receiver,
                    fail_silently=False,
                )'''

                return redirect("signin")
            else:
                messages.warning(request, "The OTP has expired, get a new OTP!")
                return redirect("verify-email", username=username)
        else:
            messages.warning(request, "Invalid OTP entered, enter a valid OTP!")
            return redirect("verify-email", username=username)

    context = {"username": username}
    return render(request, "verify_token.html", context)


def resend_otp(request):
    if request.method == 'POST':
        user_email = request.POST["otp_email"]

        if get_user_model().objects.filter(email=user_email).exists():
            user = get_user_model().objects.get(email=user_email)
            otp = OtpToken.objects.create(user=user, otp_expires_at=timezone.now() + timezone.timedelta(minutes=5))

            subject = "Email Verification"
            message = f"""
            Hi {user.username}, here is your OTP {otp.otp_code}
            it expires in 5 minutes, use the URL below to redirect back to the website
            http://127.0.0.1:8000/verify-email/{user.username}
            """
            sender = "nithes262004@gmail.com"
            receiver = [user.email,]

            send_mail(
                subject,
                message,
                sender,
                receiver,
                fail_silently=False,
            )

            messages.success(request, "A new OTP has been sent to your email-address")
            return redirect("verify-email", username=user.username)
        else:
            messages.warning(request, "This email doesn't exist in the database")
            return redirect("resend-otp")

    context = {}
    return render(request, "resend_otp.html", context)

def signin(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f"Hi {request.user.username}, you are now logged-in")
            return redirect("index")
        else:
            messages.warning(request, "Invalid credentials")
            return redirect("signin")

    return render(request, "login.html")

def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "You have successfully logged out.")
    return redirect("signin")


def update_profile(request):
    if request.user.is_authenticated:
        user = request.user
        if request.method == 'POST':
            form = UpdateProfileForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                messages.success(request, "Profile updated successfully!")
                return redirect('profile')  
        else:  
            form = UpdateProfileForm(instance=user)
    
        context = {"form": form}
        return render(request, "update_profile.html", context)
    else:
        return redirect('signin')  

def profile(request):
    if request.user.is_authenticated:
        return render(request, "profile.html")

def about(request):
    return render(request,'aboutus.html')


def menu(request):
    menus=Category.objects.filter(status=0)
    return render(request,'menu.html',{'menus':menus})
def timing(request,name):
    timings=Timing.objects.filter(category__name=name,status=0)
    return render(request,'timings.html',{'timings':timings})

def products(request, category_name, timing_name):
    items = Products.objects.filter(category__name=category_name, status=False, timing__name=timing_name)
    return render(request, 'items.html', {'items': items})

@login_required
def book_table(request):
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.save()
            return redirect('mybooks') 
    else:
        form = BookingForm() 

    return render(request, 'book_table.html', {'form': form})



@login_required
def my_books(request):
    bookings = Booking.objects.filter(user=request.user)
    return render(request, 'my_books.html', {'bookings': bookings})

def contact(request):
    return render(request,'contact.html')


def viewitem(request, category_name, timing_name, item_name):
    
    item = get_object_or_404(Products, category__name=category_name, timing__name=timing_name, name=item_name, status=False)
    return render(request, 'viewitems.html', {'item': item})

def add_to_cart(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.user.is_authenticated:
            try:
                data = json.loads(request.body)
                product_qty = data.get('item_quantity')
                product_id = data.get('pid')
                
                if not product_id:
                    return JsonResponse({'status': 'Invalid Product ID'}, status=400)
                
                product_id = int(product_id)  # Ensure product_id is an integer
                product_status = Products.objects.get(id=product_id)
                
                if product_status:
                    if Cart.objects.filter(user=request.user, product_id=product_id).exists():
                        return JsonResponse({'status': 'Product Already in Cart'}, status=200)
                    else:
                        if product_status.quantity >= product_qty:
                            Cart.objects.create(user=request.user, product_id=product_id, product_qty=product_qty)
                            return JsonResponse({'status': 'Product Added to Cart'}, status=200)
                        else:
                            return JsonResponse({'status': 'Product Stock Not Available'}, status=200)
            except json.JSONDecodeError:
                return JsonResponse({'status': 'Invalid JSON'}, status=400)
            except Products.DoesNotExist:
                return JsonResponse({'status': 'Product Not Found'}, status=404)
            except ValueError:
                return JsonResponse({'status': 'Invalid Product ID'}, status=400)
            except Exception as e:
                return JsonResponse({'status': str(e)}, status=500)
        else:
           
            return JsonResponse({'status': 'Login to Add Cart'}, status=200)
    else:
        return JsonResponse({'status': 'Invalid Access'}, status=400)

def cart(request):
    if request.user.is_authenticated:
        cart=Cart.objects.filter(user=request.user)
        return render(request,"cart.html",{'cart':cart})
    else:
        return redirect("/")
def removecart(request,id):
    cartitem=Cart.objects.get(id=id)
    cartitem.delete()
    return redirect("/cart")



def checkout(request):
   
    
            cartitems=Cart.objects.filter(user=request.user)
            total_price=0
            for item in cartitems:
                total_price=total_price+item.product.selling_price*item.product_qty

            userprofile=Profile.objects.filter(user=request.user).first()
    
            context={'cartitems':cartitems,'total_price':total_price,'userprofile':userprofile}


            return render(request,'checkout.html',context)


from .models import Order, OrderItem, Cart,Profile

from django.conf import settings
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render
from resfinal.models import CustomUser, Profile, Order, Cart, OrderItem
import random

def placeorder(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            currentuser = request.user

            if not currentuser.first_name:
                currentuser.first_name = request.POST.get('fname')
                currentuser.last_name = request.POST.get('lname')
                currentuser.save()

            
            if not Profile.objects.filter(user=request.user).exists():
                userprofile = Profile()
                userprofile.user = request.user
                userprofile.phone = request.POST.get('phone')
                userprofile.address = request.POST.get('address')
                userprofile.city = request.POST.get('city')
                userprofile.state = request.POST.get('state')
                userprofile.country = request.POST.get('country')
                userprofile.save()

            neworder = Order()
            neworder.user = request.user
            neworder.fname = request.POST.get('fname')
            neworder.lname = request.POST.get('lname')
            neworder.email = request.POST.get('email')
            neworder.phone = request.POST.get('phone')
            neworder.address = request.POST.get('address')
            neworder.city = request.POST.get('city')
            neworder.state = request.POST.get('state')
            neworder.country = request.POST.get('country')
            neworder.pincode = request.POST.get('pincode')
            neworder.payment_mode = request.POST.get('payment_mode')
            neworder.payment_id = request.POST.get('payment_id')

            cart = Cart.objects.filter(user=request.user)
            cart_total_price = 0
            for item in cart:
                cart_total_price += item.product.selling_price * item.product_qty

            neworder.total_price = cart_total_price
            trackno = 'nithes' + str(random.randint(1111111, 9999999))
            while Order.objects.filter(tracking_no=trackno).exists():
                trackno = 'nithes' + str(random.randint(1111111, 9999999))

            neworder.tracking_no = trackno
            neworder.status = 'Completed'
            neworder.save()

            
            neworderitems = Cart.objects.filter(user=request.user)
            for item in neworderitems:
                OrderItem.objects.create(
                    order=neworder,
                    product=item.product,
                    price=item.product.selling_price,
                    quantity=item.product_qty
                )

            
            Cart.objects.filter(user=request.user).delete()

            
            
            neworder.save()

            messages.success(request, "Your order has been placed successfully.")
            payMode = request.POST.get('payment_mode')
            if payMode == "Paid by Razorpay":
                return JsonResponse({'status': "Your order has been placed successfully"})

            return JsonResponse({'status': "Your order has been placed successfully"})

        else:
            return JsonResponse({'status': "Order Not placed"})

    else:
        return JsonResponse({'status': "Order Not placed"})


from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Cart  

@login_required
def razorpaycheck(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user)
        total_price = 0
        
        for item in cart:
            total_price += item.product.selling_price * item.product_qty
        
        return JsonResponse({
            'total_price': total_price
        })
    else:
        return JsonResponse({
            'error': 'User is not authenticated'
        }, status=401) 

def myorders(request):
    orders=Order.objects.filter(user=request.user)
    context={'orders':orders}

    return render(request,'my-orders.html',context)
def vieworder(request,trackno):
    order=Order.objects.filter(tracking_no=trackno).filter(user=request.user).first()
    orderitems=OrderItem.objects.filter(order=order)
    context={'order':order,'orderitems':orderitems}
    return render(request,'vieworder.html',context)



from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from io import BytesIO
import requests

def generate_pdf(request, order_id):
    # Fetch order details from the database
    order = get_object_or_404(Order, id=order_id)
    orderitems = OrderItem.objects.filter(order=order)

    # Prepare response for PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="bill-{order.id}.pdf"'

    # Create PDF document
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    
    # Company details
    p.setFont("Helvetica", 12)
    p.drawString(100, 750, "Company Name: SNK")
    p.drawString(100, 735, "Address: 1568, Church Road Kashmere Gate,")
    p.drawString(100, 720, "New Delhi, Delhi, India - 110006.")

    # Inserting logo as image
    logo_url = "https://t3.ftcdn.net/jpg/05/18/90/42/360_F_518904265_94N2jWJUNC41QaD7IduC1mahEVu9yaSn.jpg"
    try:
        logo_response = requests.get(logo_url)
        if logo_response.status_code == 200:
            logo_image = ImageReader(BytesIO(logo_response.content))
            p.drawImage(logo_image, 400, 750, width=100, height=50, preserveAspectRatio=True)
    except Exception as e:
        print(f"Failed to fetch or insert logo image: {e}")

    # Order details
    y = 700
    p.drawString(100, y, f"First Name: {order.fname}")
    p.drawString(100, y-15, f"Last Name: {order.lname}")
    p.drawString(100, y-30, f"Email: {order.email}")
    p.drawString(100, y-45, f"Phone: {order.phone}")
    p.drawString(100, y-60, f"Address:")
    p.drawString(120, y-75, f"{order.address}")
    p.drawString(120, y-90, f"{order.city}, {order.state}")
    p.drawString(120, y-105, f"{order.country} - {order.pincode}")

    # Order items
    y -= 130
    for item in orderitems:
        p.drawString(100, y, f"Product: {item.product.name}")
        p.drawString(300, y, f"Quantity: {item.quantity}")
        p.drawString(400, y, f"Price: {item.price}")
        y -= 15

    # Grand total, payment mode, status, tracking number
    y -= 30
    p.drawString(100, y, f"Grand Total: {order.total_price}")
    y -= 15
    p.drawString(100, y, f"Payment Mode: {order.payment_mode}")
    y -= 15
    p.drawString(100, y, f"Order Status: {order.status}")
    y -= 15
    p.drawString(100, y, f"Tracking Number: {order.tracking_no}")

    p.showPage()
    p.save()

    # Get PDF content from buffer and add it to response
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response






