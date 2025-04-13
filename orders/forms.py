from django import forms
from .models import Order


class CheckoutForm(forms.Form):
    phone = forms.CharField(max_length=20)
    shipping_address = forms.CharField(max_length=255)
    payment_method = forms.ChoiceField(choices=Order.payment_choices)
