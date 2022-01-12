from django.urls import path
from . import views

app_name = 'timewatchstore'

urlpatterns = [
    path('', views.index, name='index.html'),
    # path('category/<int:pk>', views.category_gender, name='category.html'),
    path('category/<int:pk>', views.category, name='category.html'),
    path('cart', views.cart, name='cart.html'),
    path('search', views.search_form, name='search.html'),
    path('price_filter', views.filter_by_prices, name='price_filter.html'),
    path('checkout', views.checkout, name='checkout.html'),
    path('confirmation', views.confirmation, name='confirmation.html'),
    path('registration', views.registration, name='registration.html'),
    path('login', views.log_in, name='login.html'),
    path('logout', views.log_out, name='logout.html'),
    path('contact', views.contact, name='contact.html'),
    path('singleproduct/<int:pk>', views.singleproduct, name='single-product.html'),
]