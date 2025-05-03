from django import forms

class CheckoutForm(forms.Form):
    email_address = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=50, required=True)
    phone_number = forms.CharField(max_length=20, required=False)
    street_address1 = forms.CharField(max_length=40, required=True)
    street_address2 = forms.CharField(max_length=40, required=False)
    town_or_city = forms.CharField(max_length=40, required=True)
    postcode = forms.CharField(max_length=20, required=False)
    country = forms.CharField(max_length=40, required=True)