from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from .models import User, Listing, Bid, Comment
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django import forms
from django.forms import ModelForm
from .forms import *

def index(request):
    listings = Listing.objects.filter(active='0').order_by('-id')
    stopped = Listing.objects.filter(active='1').order_by('id')
    context = {
        'listings': listings,
        'stopped': stopped,
    }
    return render(request, "auctions/index.html", context)

@login_required
def add_listing(request):
    if request.method == "POST":
        form = NewListingForm(request.POST, request.FILES)
        if form.is_valid():
            # get the info from the form and add user info
            new_listing = form.save(commit=False)
            new_listing.user = request.user
            new_listing.save()
            return HttpResponseRedirect(reverse("listing", args=(new_listing.id,)))
        else:
            return render(request, "auctions/add_listing.html", {
                "form": form
            })
    return render(request, "auctions/add_listing.html", {
        "form": NewListingForm
    })

def categories(request):
    if request.method == "POST":
        form = Category(request.POST)
        if form.is_valid():
            temp = form.save(commit=False)
            return render(request, 'auctions/categories.html', {
                'form': form,
                'listings': Listing.objects.filter(active='0', category=temp.category)
            })
    return render(request, 'auctions/categories.html', {
        "form": Category
    })

def watchlist(request, username):
    if request.user.is_authenticated and request.user.username == username:
        is_my_profile = True
        username = request.user
    else:
        try:
            is_my_profile = False
            username = User.objects.get(username=username)
        except User.DoesNotExist:
            return HttpResponseRedirect(reverse("profile", args=(username,)))

    return render(request, "auctions/watchlist.html", {
        "is_my_profile": is_my_profile,
        "username": username,
        "watchlist": User.objects.get(username=username).watchlist.filter(active='0')
    })

def profile(request, username):
    not_found = False
    if request.user.is_authenticated and request.user.username == username:
        # we want the profile of the logged in user; send nothing in context
        is_my_profile = True
        username = request.user
    else:
        # the profile we want to view is not the logged in user's profile
        is_my_profile = False
        try:
            username = User.objects.get(username=username)
        except User.DoesNotExist:
            not_found = True

    return render(request, "auctions/profile.html", {
        "is_my_profile": is_my_profile,
        "not_found": not_found,
        "username": username,
        "listings": Listing.objects.filter(active='0', user=User.objects.get(username=username))
        })

def listing(request, listing_id):
     # try to get the item from the database
    # and determine if the item is signed up in user's listing
    is_my_listing = False
    try:
        requested_listing = Listing.objects.get(pk=listing_id)
        if request.user.is_authenticated and request.user.username == requested_listing.user.username:
            is_my_listing = True
    except Listing.DoesNotExist:
        requested_listing = None
 # determine if the listing is in the signed in user's watchlist
    my_watchlist = False
    if request.user.is_authenticated and request.user in Listing.objects.get(pk=listing_id).watchers.all():
        my_watchlist = True

    # POST when user submits a bid, adds to watchlist, removes from watchlist, closes listing, or comments
    if request.method == "POST" and request.user.is_authenticated:
        # user submitted a bid
        if 'new-bid' in request.POST:
            form = AddBidForm(request.POST)
            if form.is_valid():
                # add the bid to the database
                new_bid = form.save(commit=False)
                new_bid.user = request.user
                new_bid.listing = Listing.objects.get(pk=listing_id)
                new_bid.save()
                return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
            else:
                return render(request, "auctions/listing.html", {
                    "my_watchlist": my_watchlist,
                    "is_my_listing": is_my_listing,
                    "listing": requested_listing,
                    "bid_form": form,
                    "comment_form": CommentForm,
                    "comments": Comment.objects.filter(listing=requested_listing)
                })
# the user added the listing to their watchlist
        elif 'add-watchlist' in request.POST:
            Listing.objects.get(pk=listing_id).watchers.add(request.user)
            return HttpResponseRedirect(reverse("watchlist", args=(request.user.username,)))

        # the user removed the listing from their watchlist
        elif 'remove-watchlist' in request.POST:
            Listing.objects.get(pk=listing_id).watchers.remove(request.user)
            return HttpResponseRedirect(reverse("listing", args=(listing_id,)))

        # the user closed the listing
        elif 'close-listing' in request.POST and is_my_listing:
            to_close = Listing.objects.get(pk=listing_id)
            to_close.active = '1'
            to_close.save()
            return HttpResponseRedirect(reverse("profile", args=(request.user.username,)))

         # the user commented on the listing
        elif 'post-comment' in request.POST:
            form = CommentForm(request.POST)
            if form.is_valid():
                # add comment to database
                new_comment = form.save(commit=False)
                new_comment.user = request.user
                new_comment.listing = Listing.objects.get(pk=listing_id)
                new_comment.save()
                return HttpResponseRedirect(reverse("listing", args=(listing_id,)))
            else:
                return render(request, "auctions/listing.html", {
                    "my_watchlist": my_watchlist,
                    "is_my_listing": is_my_listing,
                    "listing": requested_listing,
                    "bid_form": AddBidForm,
                    "comment_form": form,
                    "comments": Comment.objects.filter(listing=requested_listing)
                })

    return render(request, "auctions/listing.html", {
        "my_watchlist": my_watchlist,
        "is_my_listing": is_my_listing,
        "listing": requested_listing,
        "bid_form": AddBidForm(initial={"listing": listing_id,}),
        "comment_form": CommentForm,
        "comments": Comment.objects.filter(listing=requested_listing)
    })
def delete_listing(request, id):
    print(id)
    Listing.objects.filter(pk=id).delete()
    return render(request, 'auctions/index.html')

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    request.session.flush()
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
