from django.contrib import admin

from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "company",
        "phone",
        "email",
        "is_active",
        "created_at",
    )

    search_fields = (
        "name",
        "company",
        "phone",
        "email",
    )

    list_filter = (
        "is_active",
        "created_at",
    )

    ordering = ("-created_at",)