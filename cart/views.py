from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from timewatchstore.models import Product, SubCategory
from .cart import Cart
from .forms import CartAddProductForm

subcategory_list = SubCategory.objects.all()

@require_POST
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        cart.add(product=product,
                 quantity=cd['quantity'],
                 override_quantity=cd['override'])
    return redirect('cart:cart_detail')


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    return redirect('cart:cart_detail')


def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item['update_quantity_form'] = CartAddProductForm(initial={'quantity': item['quantity'],
                                                                   'override': True})
    username = request.session.get('username', 0)                                                               
    return render(request, 'cart/detail.html', {'cart': cart, 
                                                'username': username,
                                                'subcategories': subcategory_list})
