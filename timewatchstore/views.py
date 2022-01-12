from django.http import HttpResponse
from django.shortcuts import render
from itertools import islice
from . import forms
from . import models

from cart.forms import CartAddProductForm

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


import datetime
import re
import pandas as pd
import os
from django.conf import settings

# Phân trang
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Count, F, Value

# thư viện cho việc sử dụng email
from TimeWatch.settings import EMAIL_HOST_USER
from django.core.mail import message, send_mail
from django.core.mail import EmailMultiAlternatives

# Global var

subcategory_list = models.SubCategory.objects.all()
# brand_category = models.BrandCategory.objects.all()
gendercategory_list = models.GenderCategory.objects.all()
brandcategory_list = models.BrandCategory.objects.all()
subcategory = 0
search_str = ''

# Create your views here.
def index(request):
    username = request.session.get('username', 0)
    product_list = models.Product.objects.order_by("-public_day")
    most_viewed_list = models.Product.objects.order_by("-viewed")[:8]
    newest = product_list[0]
    eight_newest = product_list[:8]
    eight_oldest = list(islice(reversed(product_list),0,8))

    
    return render(request, "timewatchstore/index.html",
                  {'newest': newest,
                   'eight_oldest': eight_oldest,
                   'eight_newest': eight_newest,
                   'most_viewed_list': most_viewed_list,
                   'subcategories': subcategory_list,
                   'username': username,
                   })

def filter_by_prices(request):
    username = request.session.get('username', 0)
    global subcategory
    global search_str
    product_items = 0
    # vào được đến đây
    product_list = models.Product.objects.all().order_by("price")
    ###
    result = "chua nhan gi ca"
    three_newest = models.Product.objects.all().order_by("-public_day")[:3]
    if request.method == 'GET':
        result = "da nhan GET"
        subcategory = request.GET.get('subcategory_id_1')
        x = 'yes'
        if request.GET.get('name_1'):
            search_str = request.GET.get('name_1')
        else:
            search_str = ''
            x = 'no'
        a = float(request.GET.get('price_from'))
        b = float(request.GET.get('price_to'))
        price_from = a
        price_to = b
        if(a > b):
            price_from = b
            price_to = a

        if subcategory != '0':
            result = " da nhan category " + \
                str(subcategory) + " - " + \
                str(price_from) + " - " + str(price_to)
            if(x != 'no'):
                product_list = models.Product.objects.filter(
                    name__contains=search_str, subcategory=subcategory).order_by("price")
            else:
                product_list = models.Product.objects.filter(
                    subcategory=subcategory).order_by("price")

        if subcategory == '0':
            result = " da nhan category = 0" + str(subcategory)
            if(x != 'no'):
                product_list = models.Product.objects.filter(
                    name__contains=search_str).order_by("price")

        product_list = [product for product in product_list if product.price >=
                        price_from and product.price <= price_to]

        product_items = len(product_list)

        result = 'từ ' + \
            '{:20,.0f}'.format(price_from) + ' đ đến ' + \
            '{:20,.0f}'.format(price_to) + ' đ'

        page = request.GET.get('page', 1)
        paginator = Paginator(product_list, 9)  # so product/trang

        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)

        return render(request, "timewatchstore/category.html",
                      {'three_newest': three_newest,
                       'subcategories': subcategory_list,
                       'products': products,
                       'pk': subcategory,
                       'product_items': product_items,
                       'subcategory': subcategory,
                       'search_str': search_str,
                       'result': result,
                       'username': username
                       })


def singleproduct(request,pk):
    username = request.session.get('username', 0)
    # slugname = models.Product.objects.get(name_url = slugname)
    product_select = models.Product.objects.get(pk=pk)

    # khi người dùng chọn xem 1 sản phẩm > tăng view của sản phẩm thêm 1
    models.Product.objects.filter(
        pk=product_select.pk).update(viewed=F('viewed') + 1)
    product_select.refresh_from_db()

    cart_product_form = CartAddProductForm()
    # # doc rule.csv
    # rules = pd.read_csv(os.path.join(settings.MEDIA_ROOT,'timewatchstore/rules.csv'),squeeze=True, index_col=0)
    # lst = rules.values.tolist()
    # list_rule = []
    # for item in lst:
    #     result = item
    #     if str(pk) in re.findall('\d+[, \d+]*',item[0])[0].split(','):
    #         list_rule = re.findall('\d+[, \d+]*',item[1])[0].split(',')
    # list_asc_products = []
    # for i in list_rule:
    #     list_asc_products.append(models.Product.objects.get(pk=int(i)))
    return render(request, "timewatchstore/single-product.html",
                  {'product': product_select,
                    # 'name_url':slugname,
                   'subcategories': subcategory_list,
                   'username': username,
                    'cart_product_form': cart_product_form,
                #    'list_asc_products': list_asc_products,
                #    'list_rule': list_rule,
                }
                )


def category(request, pk):
    username = request.session.get('username', 0)
    subcategory = pk
    product_list = []
    subcategory_name = ''
    
    if pk != 0:
        product_list = models.Product.objects.filter(
            subcategory=pk).order_by("-public_day")
        selected_sub = models.SubCategory.objects.get(pk=pk)
        subcategory_name = selected_sub.name
    else:
        product_list = models.Product.objects.order_by("-public_day")

    three_newest = product_list[:3]

    page = request.GET.get('page', 1)  # trang bat dau
    paginator = Paginator(product_list, 9)  # so product/trang
    # paginator_15 = Paginator(product_list, 15)
    # paginator_12 = Paginator(product_list, 12)
    # paginator_9 = Paginator(product_list, 9)

    try:
        products = paginator.page(page)
        # products_15 = paginator_15.page(page)
        # products_12 = paginator_12.page(page)
        # products_9 = paginator_9.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    return render(request, "timewatchstore/category.html",
                  {'three_newest': three_newest,
                   'subcategories': subcategory_list,
                   'subcategory_name': subcategory_name,
                   'subcategories': subcategory_list,
                   'products': products,
                #    'products_15': products_15,
                #    'products_12': products_12,
                #    'products_9': products_9,
                   'pk': pk,
                   'username': username
                   }
                   )

# def category_gender(request, pk):
#     username = request.session.get('username', 0)
#     gender_category = pk
#     product_list = []
#     subcategory_name = ''
    
#     if pk != 0:
#         product_list = models.Product.objects.filter(
#             gender_category=pk).order_by("-public_day")
#         selected_sub = models.GenderCategory.objects.get(pk=pk)
#         subcategory_name = selected_sub.name
#     else:
#         product_list = models.Product.objects.order_by("-public_day")

#     three_newest = product_list[:3]

#     page = request.GET.get('page', 1)  # trang bat dau
#     paginator = Paginator(product_list, 6)  # so product/trang

#     try:
#         products = paginator.page(page)
#     except PageNotAnInteger:
#         products = paginator.page(1)
#     except EmptyPage:
#         products = paginator.page(paginator.num_pages)

#     return render(request, "timewatchstore/category.html",
#                   {'three_newest': three_newest,
#                    'subcategory_name': subcategory_name,
#                    'subcategories_gender': gendercategory_list,
#                    'products': products,
#                    'pk': pk,
#                    'username': username
#                    }
#                    )

def search_form(request):
    username = request.session.get('username', 0)
    global subcategory
    global search_str
    product_items = 0
    three_newest = models.Product.objects.all().order_by("-public_day")[:3]
    product_list = []
    if request.method == 'GET':
        form = forms.FormSearch(request.GET, models.Product)

        if form.is_valid():
            subcategory = form.cleaned_data['subcategory_id']
            search_str = form.cleaned_data['name']
            if subcategory != 0:
                product_list = models.Product.objects.filter(
                    subcategory=subcategory, name__contains=search_str).order_by("-public_day")
            else:
                product_list = models.Product.objects.filter(
                    name__contains=search_str).order_by("-public_day")

        product_items = len(product_list)

        page = request.GET.get('page', 1)
        paginator = Paginator(product_list, 6)  # so product/trang

        try:
            products = paginator.page(page)
        except PageNotAnInteger:
            products = paginator.page(1)
        except EmptyPage:
            products = paginator.page(paginator.num_pages)

        return render(request, "timewatchstore/category.html",
                      {'three_newest': three_newest,
                       'subcategories': subcategory_list,
                       'products': products,
                       'pk': subcategory,
                       'product_items': product_items,
                       'subcategories': subcategory_list,
                       'subcategory': subcategory,
                       'search_str': search_str,
                       'username': username
                       })


def cart(request):
    
    return render(request, "timewatchstore/cart.html")

def contact(request):
    username = request.session.get('username', 0)
    now = datetime.datetime.now()
    fullname = request.session.get('fullname', 0)
    if request.method == 'POST':
        form_contact = forms.ContactForm(request.POST, models.Contact)
        if (form_contact.is_valid()):
            form_contact.save()
            email_address = form_contact.cleaned_data['email']
            subject = 'Welcome to TimeWatch'
            message = 'Hope you are enjoying our service'
            recepient = str(email_address)

            html_content = 'Kính chào <h3><b>'+ form_contact.cleaned_data['fullname']+',</b></h3>'\
                            + '<p>Chào mừng quý khách đến với <strong>TimeWatch</strong> website.</p>' \
                            + '<h4><strong>Chúng tôi đã tiếp nhận được thông tin của quý khách. Chúng tôi sẽ thông báo thông tin đến quý khách một cách nhanh nhất.<br>Xin Cảm Ơn Quý Khách đã ủng hộ TIMEWATCH STORE</strong></h4>'\
                            + '<h4 style="color:red">'+ message +'</h4>'      
            
            msg = EmailMultiAlternatives(subject, message, EMAIL_HOST_USER, [recepient])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            result = 'Our mail was sent to your mail box. Thank you'

            return render(request, 'timewatchstore/contact.html',
                    {'subcategories': subcategory_list,
                    'username': username, 
                    'form_contact': form_contact,
                    'today': now,
                    'fullname': fullname,
                    'result': result,
                    }
                    )
        else:
            form_contact = forms.ContactForm()


    return render(request, 'timewatchstore/contact.html',
                  {'subcategories': subcategory_list, 
                  'username': username,
                   'today': now,
                   'fullname': fullname,
                   }
                  )

def checkout(request):
    
    return render(request, "timewatchstore/checkout.html")

def confirmation(request):
    
    return render(request, "timewatchstore/confirmation.html")

def log_in(request):
    if request.method == "POST":
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            result = "Welcome back "  + username
            request.session['username'] = username
            username = request.session.get('username', 0)
            return render(request, "timewatchstore/login.html", {'login_result': result,
                                                        'username': username,'subcategories': subcategory_list,'first_name': first_name,'last_name':last_name,
                                                        })
        else:
            print("You can't login.")
            print("Username: {} and password: {}".format(username, password))
            login_result = "Username hoặc password không chính xác!"
            return render(request, "timewatchstore/login.html", {'login_result': login_result, 'subcategories': subcategory_list,})
    else:
        return render(request, "timewatchstore/login.html", {'subcategories': subcategory_list})

@login_required
def log_out(request):
    # try:
    #     del request.session['username']
    # except KeyError:
    #     pass
    # logout = "Quý khách đã logout. Quý khách có thể login trở lại"
    # return render(request, "store/login.html", {'logout': logout})
    logout(request)
    result = "Quý khách đã logout. Quý khách có thể login trở lại"
    return render(request, "timewatchstore/login.html", {'logout_result': result, 'subcategories': subcategory_list,})

def registration(request):
    # registered = False
    # if request.method == "POST":
    #     form_cus = forms.FormCustumer(data=request.POST)
    #     if (form_cus.is_valid() and (form_cus.cleaned_data['password'] == form_cus.cleaned_data['confirm'])):
    #         user = form_cus.save()
    #         user.save()
    #         registered = True

    #     if (form_cus.cleaned_data['password'] != form_cus.cleaned_data['confirm']):
    #         form_cus.add_error('confirm', 'Password và confirm password khác nhau!!!')
    #         print(form_cus.errors)
    # else:
    #     form_cus = forms.FormCustumer()

    registered = False
    if request.method == "POST":
        form_user = forms.UserForm(data=request.POST)
        form_por = forms.UserProfileInfoForm(data=request.POST)
        if (form_user.is_valid() and form_por.is_valid() and form_user.cleaned_data['password'] == form_user.cleaned_data['confirm']):
            user = form_user.save()
            user.set_password(user.password)
            user.save()

            profile = form_por.save(commit=False)
            profile.user = user
            if 'image' in request.FILES:
                profile.image = request.FILES['image']
            profile.save()
            registered = True

            # Gửi email 
            email_address = form_user.cleaned_data['email']        
            subject = 'Tài khoản của Quý khách tại TimeWatch Store đã được tạo.'
            message = 'Hãy trải nghiệm việc mua sắm online tại TIMEWATCH STORE.<br/> Trân trọng.'
            recepient = str(email_address)

            html_content = '<h2 style="color:blue"><i>Kính chào '+ form_user.cleaned_data['username']+',</i></h2>'\
                        + '<p>Chào mừng quý khách đến với <strong>TIMEWATCH STORE</strong> website.</p>' \
                        + '<h4 style="color:red">'+ message +'</h4>'      
        
            msg = EmailMultiAlternatives(subject, message, EMAIL_HOST_USER, [recepient])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

        if form_user.cleaned_data['password'] != form_user.cleaned_data['confirm']:
            form_user.add_error(
                'confirm', 'Password và confirm password không giống nhau!')
            print(form_user.errors, form_por.errors)
    else:
        form_user = forms.UserForm()
        form_por = forms.UserProfileInfoForm()

    username = request.session.get('username', 0)
    return render(request, 'timewatchstore/registration.html',
                  {'subcategories': subcategory_list,
                   'form_user': form_user,
                   'form_por': form_por,
                   'registered': registered,
                   'username': username}
                  )

