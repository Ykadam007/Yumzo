from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):

    rating = forms.ChoiceField(
        choices=[
            (5, '⭐⭐⭐⭐⭐ Excellent'),
            (4, '⭐⭐⭐⭐ Very Good'),
            (3, '⭐⭐⭐ Good'),
            (2, '⭐⭐ Fair'),
            (1, '⭐ Poor'),
        ],
        widget=forms.Select(
            attrs={
                'class': 'form-select'
            }
        )
    )

    comment = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Share your experience...'
            }
        )
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment']