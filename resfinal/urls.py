from django.urls import path
from . import views 



urlpatterns = [
    path("", views.index, name="index"),
    path("register", views.signup, name="register"),
    path("verify-email/<slug:username>", views.verify_email, name="verify-email"),
    path("resend-otp", views.resend_otp, name="resend-otp"),
    path("login", views.signin, name="signin"),
    path("logout", views.logout_page, name="logout"),
    path("profile/update", views.update_profile, name="update-profile"),
    path("profile", views.profile, name="profile"),
    path("about", views.about, name="about"),
    path("menu", views.menu, name="menu"),
    path("menu/<str:name>", views.timing, name="timing"),
    path("menu/<str:category_name>/<str:timing_name>", views.products, name="products"),
    path("booking", views.book_table, name="book_table"), 
    path("mybooks", views.my_books, name="mybooks"),  
    path("contact", views.contact, name="contact"),  
    path("menu/<str:category_name>/<str:timing_name>/<str:item_name>", views.viewitem, name="viewitem"),   
    path('addtocart',views.add_to_cart,name="addtocart"),
    path('cart',views.cart,name='cart'),
    path('removecart/<str:id>',views.removecart,name='removecart'),
    path('checkout',views.checkout,name='checkout'),
    path('place-order',views.placeorder,name='placeorder'),
    path('proceed-to-pay',views.razorpaycheck),
    path('my-orders', views.myorders, name='my-orders'),
    path('view-order/<str:trackno>',views.vieworder,name='orderview'),
    path('download-pdf/<int:order_id>/', views.generate_pdf, name='download_pdf'),
   
   
]

