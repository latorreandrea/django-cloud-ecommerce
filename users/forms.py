from django import forms
from .models import UserProfile

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ('user',)
        fields = (
            'full_name', 'contact_email', 'phone_number', 'town_or_city',
            'street_address1', 'street_address2',
            'country', 'county', 'postcode')
    
    def __init__(self, *args, **kwargs):
        '''add placeholders, '''
        super().__init__(*args, **kwargs)
        placeholders = {
            'full_name': 'Full Name',
            'contact_email': 'Contact Email', 
            'phone_number': 'Phone Number', 
            'town_or_city': 'City', 
            'street_address1': 'main Street Adress', 
            'street_address2': 'secondary Street Adress',
            'country': 'Country', 
            'county': 'County/Region',
            'postcode': 'Postal Code',
        }
        for field in self.fields:
            if field in placeholders:
                self.fields[field].widget.attrs['placeholder'] = placeholders.get(field, '')