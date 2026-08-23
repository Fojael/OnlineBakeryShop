from django.contrib import admin

from .models import Wishlist
from .models import WishlistItem


class WishlistItemInline(
    admin.TabularInline
):
    model = WishlistItem
    extra = 0


@admin.register(Wishlist)
class WishlistAdmin(
    admin.ModelAdmin
):
    list_display = (
        "id",
        "customer",
        "created_at",
    )

    search_fields = (
        "customer__email",
    )

    inlines = [
        WishlistItemInline,
    ]


@admin.register(WishlistItem)
class WishlistItemAdmin(
    admin.ModelAdmin
):
    list_display = (
        "id",
        "wishlist",
        "product",
        "created_at",
    )

    search_fields = (
        "product__name",
        "wishlist__customer__email",
    )