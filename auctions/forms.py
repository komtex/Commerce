
from django import forms
from django.forms import ModelForm
from django.db import models
from auctions.models import User, Listing, Bid, Comment
from django.core.exceptions import ValidationError

STATUS = (
    ('0', 'Active'),
    ('1', 'Sold'),
)
CATEGORIES = (
        ('0', 'No Category'),
        ('1', 'Arts'),
        ('2', 'Books'),
        ('3', 'DVDs'),
        ('4', 'Electronics'),
        ('5', 'Fashion'),
        ('6', 'Health'),
        ('7', 'Home'),
        ('8', 'Music'),
        ('9', "Toys"),
        ('10', "Video Games")
    )

class AddBidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['listing', 'amount']
        widgets = {
            'amount': forms.TextInput(attrs={'placeholder': 'Bid', 'class': 'form-control'}),
            'listing': forms.HiddenInput()
        }
    def clean_amount(self):
        bid_amount = self.cleaned_data["amount"]
        price = Listing.objects.get(pk=self.data["listing"]).get_price()
        if bid_amount <= price:
            raise ValidationError(
                'Bid must be higher than the current price.',
                code='Invalid'
            )
        return bid_amount

class NewListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['title', 'description', 'start_price', 'image', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'cols': 80, 'rows': 8, 'class': 'form-control'}),
            'start_price': forms.NumberInput(attrs={'placeholder': 'price', 'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'})
        }

class Category(ModelForm):
    class Meta:
        model = Listing
        fields = ['category']
        widgets = {
        'category': forms.Select(attrs={'class': 'form-control'})
        }

class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
        'content': forms.Textarea(attrs={'placeholder': 'Your Comment', 'rows': 6, 'class': 'form-control'})
        }
