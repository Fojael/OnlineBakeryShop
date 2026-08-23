from django.urls import path

from .views import WishlistItemView
from .views import WishlistView

urlpatterns = [

    path(
        "",
        WishlistView.as_view(),
        name="wishlist",
    ),

    path(
        "<int:item_id>/",
        WishlistItemView.as_view(),
        name="wishlist-item",
    ),

]