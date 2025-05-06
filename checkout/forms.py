from django import forms
from .models import Order, OrderItem
from products.models import Product
# https://pypi.org/project/django-countries/#the-country-object
from django_countries.widgets import CountrySelectWidget


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = (
            'full_name', 'email_address', 'phone_number', 'town_or_city',
            'street_address1', 'street_address2',
            'country', 'county', 'postcode',
            # Billing Info
            'billing_full_name', 'billing_email_address', 'billing_phone_number',
            'billing_street_address1', 'billing_street_address2',
            'billing_town_or_city', 'billing_county', 
            'billing_postcode', 'billing_country'
            )
        widgets = {'country': CountrySelectWidget()}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            # Shipment Info
            'full_name': 'Full Name',
            'email_address': 'email@email.example',
            'phone_number': 'Phone Number',
            'town_or_city': 'City',
            'street_address1': 'Main Street Address',
            'street_address2': 'Secondary Street Address',
            'country': 'Country',
            'county': 'County/Region',
            'postcode': 'Postal Code',
            # Billing Info
            'billing_full_name': 'Full Name',
            'billing_email_address': 'Email',
            'billing_phone_number': 'Phone Number',
            'billing_town_or_city': 'City',
            'billing_street_address1': 'Main Street Address',
            'billing_street_address2': 'Secondary Street Address',
            'billing_country': 'Country',
            'billing_county': 'County/Region',
            'billing_postcode': 'Postal Code',
        }
        self.fields['full_name'].widget.attrs['autofocus'] = True
        for field in self.fields:
            if self.fields[field].required:
                placeholder = f'{placeholders[field]} *'
            else:
                placeholder = f'{placeholders[field]}'
            self.fields[field].widget.attrs['class'] = 'stripe-style-input'
            self.fields[field].widget.attrs['placeholder'] = placeholder
            self.fields[field].label = False