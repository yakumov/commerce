from django import forms
from django.db.models import fields
from .models import LotImage

class LotImageForm(forms.ModelForm):
    class Meta:
        model = LotImage
        fields = ['titleimage', 'lot_image']