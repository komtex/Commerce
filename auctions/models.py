from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator
# from django.core.exceptions import ValidationError

""" def file_path(instance, filename):
    return 'user_{0}/{1}'.format(instance.user.id, filename)
"""
class User(AbstractUser):
    pass
    show_email=models.BooleanField(null=False, default=False)
    website=models.URLField(max_length=250, blank=True)
    instagram=models.SlugField(blank=True)
    location=models.CharField(max_length=60, blank=True)

class Listing(models.Model):
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

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, related_name='listings')
    image = models.FileField( upload_to='images/', blank=True, default="")
    title = models.CharField(max_length=60, blank=False)
    description = models.CharField(max_length=540, blank=False)
    start_price = models.DecimalField(max_digits=10, decimal_places=2, blank=False, validators=[MinValueValidator(0)])
    time_create = models.DateTimeField(auto_now_add=True)
    watchers = models.ManyToManyField(User, blank=True, related_name="watchlist")
    active = models.CharField(
                                    ('STATUS'),
                                    max_length=30,
                                    choices=STATUS,
                                    default=STATUS[0][0]
                                    )
    category = models.CharField(
                            ('Categories'),
                            max_length=30,
                            choices=CATEGORIES,
                            default=CATEGORIES[0][0]
                            )
    def __str__(self):
        return f"{self.title} by {self.user.username}"

    def get_price(self):
        price = self.bids.order_by('-amount').first()
        if price is None:
            price = self.start_price
        else:
            price = price.amount
        return price

    def get_highest_bidder(self):
        if self.start_price != self.get_price():
            return self.bids.order_by('-amount').first().user
        else:
            return None

class Bid(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name="bids", null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="bids", null=True)
    amount = models.DecimalField(decimal_places=2, max_digits=10, blank=False, validators=[MinValueValidator(0)])
    time_placed = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: ${self.amount} on {self.listing.title}"

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name='comments')
    content = models.CharField(max_length=280, blank=False)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, null=True, related_name='comments')
    time_post = models.DateTimeField(auto_now_add=True)

def __str__(self):
    return f"{self.user.username} on {self.listing.title}"
