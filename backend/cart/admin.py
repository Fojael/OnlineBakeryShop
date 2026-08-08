from django.contrib import admin

from .models import Cart, CartItem


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "customer",
        "created_at",
        "updated_at",
    ]

    search_fields = [
        "customer__email",
        "customer__username",
    ]


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "cart",
        "product",
        "quantity",
        "created_at",
    ]

    search_fields = [
        "product__name",
        "cart__customer__email",
    ]