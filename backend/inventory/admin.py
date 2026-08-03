from django.contrib import admin
from .models import Inventory


@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):

    list_display = (
        "product",
        "current_stock",
        "minimum_stock",
        "updated_at",
    )

    search_fields = (
        "product__name",
    )

    list_filter = (
        "updated_at",
    )