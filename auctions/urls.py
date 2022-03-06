from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("add_listing", views.add_listing, name="add_listing"),
    path("listing/<int:listing_id>", views.listing, name="listing"),
    path("delete/<int:id>", views.delete_listing, name="delete_listing"),
    path("categories", views.categories, name='categories'),
    path("user/<str:username>", views.profile, name="profile"),
    path("user/<str:username>/watchlist", views.watchlist, name="watchlist")
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

"""
urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
"""
