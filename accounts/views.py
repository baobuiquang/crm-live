from operator import imod
from unicodedata import name
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.contrib import messages

from .models import *
from .forms import *
from .filters import *
from .decorators import *

# Create your views here.

@unauthenticated_user
def registerPage(request):
    reg_form = CreateUserForm() # UserCreationForm(), new from forms.py

    if request.method == 'POST':
        reg_form = CreateUserForm(request.POST)
        if reg_form.is_valid():
            user = reg_form.save()

            # # # ===== Handled by signals =====
            # # Initialize the user role
            # group = Group.objects.get(name = 'customer')
            # user.groups.add(group)
            # # Initialize the user 1-1 relationship
            # Customer.objects.create(
            #     user = user # user in Customer model = user variable above
            # )

            messages.success(request, 'Account was created successfully!')
            return redirect('login')
    # else:    
    return render(
        request, 'accounts/register.html',
        {
            'reg_form': reg_form,
        }
    )

@unauthenticated_user
def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username = username, password = password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.info(request, 'Username or password is incorrect!')
    # else: 
    return render(
        request, 'accounts/login.html',
        {

        }
    )

def logoutUser(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
# @allowed_user(allowed_roles = ['admin'])
@admin_only
def home(request):
    orders = Order.objects.all()
    customers = Customer.objects.all()

    return render(
        request, 'accounts/dashboard.html',
        {
            # Objects
            'orders': orders,
            'customers': customers,
            # Stat
            'total_orders': orders.count(),
            'delivered_orders': orders.filter(status='Delivered').count(),
            'pending_orders': orders.filter(status='Pending').count(),
            'total_customers': customers.count(),
        }
    )

@login_required(login_url='login')
@allowed_user(allowed_roles = ['customer'])
def userPage(request):

    ords = request.user.customer.order_set.all()

    return render(
        request, 'accounts/user.html',
            {
                'ords': ords,
                # Stat
                'total_orders': ords.count(),
                'delivered_orders': ords.filter(status='Delivered').count(),
                'pending_orders': ords.filter(status='Pending').count(),
            }
    )




@login_required(login_url='login')
@allowed_user(allowed_roles = ['customer'])
def accountSettings(request):

    acc_form = CustomerForm(instance = request.user.customer)

    if request.method == 'POST':
        acc_form = CustomerForm(
            request.POST,
            request.FILES,
            instance = request.user.customer,
        )
        if acc_form.is_valid():
            acc_form.save()

    return render(
        request, 'accounts/account_settings.html',
            {
                'acc_form': acc_form,
            }
    )




@login_required(login_url='login')
# @allowed_user(allowed_roles = ['admin'])
@admin_only
def products(request):
    products = Product.objects.all()
    return render(
        request, 'accounts/products.html',
        {
            'products': products,
        }
    )

@login_required(login_url='login')
# @allowed_user(allowed_roles = ['admin'])
@admin_only
def customer(request, customer_id):
    cstm = Customer.objects.get(id=customer_id)
    ords = cstm.order_set.all()

    myFilter = OrderFilter(
        request.GET,
        queryset = ords,
    ) # from filters.py
    ords = myFilter.qs

    return render(
        request, 'accounts/customer.html',
        {
            'customer': cstm,
            'orders': ords,
            'orders_count': ords.count(),
            'myFilter': myFilter,
        }
    )

@login_required(login_url='login')
# @allowed_user(allowed_roles = ['admin'])
@admin_only
def createOrder(request):

    ord_form = OrderForm()

    if request.method == 'POST':
        print(f">> {request.POST}")
        ord_form = OrderForm(request.POST)
        if ord_form.is_valid():
            ord_form.save()
            return redirect('/')
    else:
        return render(
            request, 'accounts/order_form.html',
            {
                'ord_form': ord_form,
            }
        )

@login_required(login_url='login')
# @allowed_user(allowed_roles = ['admin'])
@admin_only
def createOrderForACustomer(request, customer_id):

    OrderFormSet = inlineformset_factory(
        Customer, Order,
        fields = ('product', 'status'),
        extra = 5,
    )

    cstm = Customer.objects.get(id = customer_id)

    # ord_form = OrderForm(
    #     initial = {'customer': cstm}  # same as createOrder, but pre-fill here
    # )
    ord_formset = OrderFormSet(
        instance = cstm,                 # This will pre-fill, even with customer's old orders
        queryset = Order.objects.none(), # This will hide the old orders
    )

    if request.method == 'POST':
        print(f">> {request.POST}")
        # ord_form = OrderForm(request.POST)
        ord_formset = OrderFormSet(
            request.POST,
            instance = cstm,
        )
        if ord_formset.is_valid():
            ord_formset.save()
            return redirect('/')
    else:
        return render(
            request, 'accounts/order_form.html',
            {
                'ord_form': ord_formset,
            }
        )

@login_required(login_url='login')
# @allowed_user(allowed_roles = ['admin'])
@admin_only
def updateOrder(request, order_id):

    ord = Order.objects.get(id = order_id)
    ord_form = OrderForm(instance = ord)     # same as create order but pre-fill the info of this order

    print(f'>> ord: {ord}')
    print(f'>> ord_form: {ord_form}')

    if request.method == 'POST':
        print(f">> {request.POST}")
        ord_form = OrderForm(request.POST, instance = ord)
        if ord_form.is_valid():
            ord_form.save()
            return redirect('/')
    else:
        return render(
            request, 'accounts/order_form.html',
            {
                'ord_form': ord_form,
            }
        )



@login_required(login_url='login')
# @allowed_user(allowed_roles = ['admin'])
@admin_only
def deleteOrder(request, order_id):
    ord = Order.objects.get(id = order_id)
    # ord_form = OrderForm(instance = ord)     # same as create order but pre-fill the info of this order

    if request.method == 'POST':
        print(f">> {request.POST}")
        ord.delete()
        return redirect('/')
    else:
        return render(
            request, 'accounts/delete_order.html',
            {
                'ord': ord,
            }
        )