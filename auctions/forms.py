from django import forms
from .models import Painting, Bid

class PaintingForm(forms.ModelForm):
    class Meta:
        model = Painting
        fields = ['title', 'description', 'style', 'starting_price', 'image']

class BidForm(forms.ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']
