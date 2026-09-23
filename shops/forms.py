from django import forms

from .models import Shop


class ShopForm(forms.ModelForm):

    class Meta:
        model = Shop

        fields = [
            'name',
            'description',
            'phone',
            'address',
            'city',
            'pincode',
            'latitude',
            'longitude',
            'opening_time',
            'closing_time',
        ]

        widgets = {

            'description': forms.Textarea(
                attrs={
                    'rows': 4,
                    'placeholder': 'Describe your shop'
                }
            ),

            'address': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'Enter complete address'
                }
            ),

            'opening_time': forms.TimeInput(
                attrs={
                    'type': 'time'
                }
            ),

            'closing_time': forms.TimeInput(
                attrs={
                    'type': 'time'
                }
            ),

            'latitude': forms.NumberInput(
                attrs={
                    'step': 'any',
                    'placeholder': 'Example: 20.0059'
                }
            ),

            'longitude': forms.NumberInput(
                attrs={
                    'step': 'any',
                    'placeholder': 'Example: 73.7897'
                }
            ),
        }