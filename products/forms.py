from django import forms
from .models import Product, Category

class ProductForm(forms.ModelForm):
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True).order_by('name')
    )

    class Meta:
        model = Product
        fields = [
            'category',
            'name',
            'description',
            'price',
            'discount_price',
            'stock',
            'image',
            'is_available',
        ]

        widgets = {
            'category': forms.Select(
                attrs={'class': 'form-select'}
            ),

            'name': forms.TextInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter product name'
                }
            ),

            'description': forms.Textarea(
                attrs={
                    'class': 'form-control',
                    'rows': 4,
                    'placeholder': 'Describe your product'
                }
            ),

            'price': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Enter price',
                    'step': '0.01'
                }
            ),

            'discount_price': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Optional discount price',
                    'step': '0.01'
                }
            ),

            'stock': forms.NumberInput(
                attrs={
                    'class': 'form-control',
                    'placeholder': 'Available quantity',
                    'min': '0'
                }
            ),

            'image': forms.ClearableFileInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'is_available': forms.CheckboxInput(
                attrs={
                    'class': 'form-check-input'
                }
            ),
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields['category'].queryset = Category.objects.filter(
            is_active=True
        ).order_by('name')

        self.fields['category'].empty_label = 'Select Category'