from django.contrib import admin

from .models import Address


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "customer",
        "full_name",
        "phone",
        "division",
        "district",
        "is_default",
        "created_at",
    )

    list_filter = (
        "division",
        "district",
        "is_default",
    )

    search_fields = (
        "customer__username",
        "full_name",
        "phone",
    )

    ordering = (
        "-created_at",
    )
    
