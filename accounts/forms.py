from django import forms
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import *

class OrderForm(ModelForm):
    class Meta:
        model = Order
        # fields = ['customer', 'product', 'date_created', 'status']
        fields = '__all__'

class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        # fields = ['customer', 'product', 'date_created', 'status']
        fields = ['username', 'email', 'password1', 'password2']

class CustomerForm(ModelForm):
	class Meta:
		model = Customer
		fields = '__all__'
		exclude = ['user']