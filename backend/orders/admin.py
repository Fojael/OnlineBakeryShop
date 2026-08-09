from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "customer",
        "total_amount",
        "status",
        "created_at",
    )

    search_fields = (
    "customer__username",
    "customer__email",
    )

    list_filter = (
        "status",
        "created_at",
    )

    ordering = ("-created_at",)