from django import forms
from  django.contrib.auth.forms import UserCreationForm
from .models import CustomUser


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    phone =forms.CharField(
        max_length=15,
        required=True
    )

    role = forms.ChoiceField(
        choices=[
            ('customer','Customer'),
            ('shop_owner','Shop Owner'),

        ],
        required=True
    )

    class Meta:
        model= CustomUser
        fields=[
            'username',
            'email',
            'phone',
            'role',
            'password1',
            'password2',
        ]

class ProfileForm(forms.ModelForm):

    class Meta:
        model = CustomUser
        fields = [
            'username',
            'email',
            'phone',
        ]

        widgets = {
            'username': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'email': forms.EmailInput(
                attrs={
                    'class': 'form-control'
                }
            ),

            'phone': forms.TextInput(
                attrs={
                    'class': 'form-control'
                }
            ),
        }