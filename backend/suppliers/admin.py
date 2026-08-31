from django.contrib import admin
from django.utils import timezone

from .models import Supplier


# ==========================================================
# APPROVE SUPPLIERS
# ==========================================================

@admin.action(
    description="Approve selected suppliers"
)
def approve_suppliers(
    modeladmin,
    request,
    queryset,
):

    for supplier in queryset.select_related("user"):

        supplier.is_approved = True
        supplier.approved_at = timezone.now()
        supplier.approved_by = request.user

        supplier.save(
            update_fields=[
                "is_approved",
                "approved_at",
                "approved_by",
            ]
        )

        if supplier.user:

            supplier.user.is_active = True

            supplier.user.save(
                update_fields=[
                    "is_active",
                ]
            )


# ==========================================================
# REMOVE APPROVAL
# ==========================================================

@admin.action(
    description="Remove supplier approval"
)
def unapprove_suppliers(
    modeladmin,
    request,
    queryset,
):

    for supplier in queryset.select_related("user"):

        supplier.is_approved = False
        supplier.approved_at = None
        supplier.approved_by = None

        supplier.save(
            update_fields=[
                "is_approved",
                "approved_at",
                "approved_by",
            ]
        )

        if supplier.user:

            supplier.user.is_active = False

            supplier.user.save(
                update_fields=[
                    "is_active",
                ]
            )


# ==========================================================
# ACTIVATE SUPPLIERS
# ==========================================================

@admin.action(
    description="Activate selected suppliers"
)
def activate_suppliers(
    modeladmin,
    request,
    queryset,
):

    for supplier in queryset.select_related("user"):

        supplier.is_active = True

        supplier.save(
            update_fields=[
                "is_active",
            ]
        )

        if supplier.user:

            supplier.user.is_active = True

            supplier.user.save(
                update_fields=[
                    "is_active",
                ]
            )


# ==========================================================
# DEACTIVATE SUPPLIERS
# ==========================================================

@admin.action(
    description="Deactivate selected suppliers"
)
def deactivate_suppliers(
    modeladmin,
    request,
    queryset,
):

    for supplier in queryset.select_related("user"):

        supplier.is_active = False

        supplier.save(
            update_fields=[
                "is_active",
            ]
        )

        if supplier.user:

            supplier.user.is_active = False

            supplier.user.save(
                update_fields=[
                    "is_active",
                ]
            )


# ==========================================================
# SUPPLIER ADMIN
# ==========================================================

@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "name",
        "company",
        "email",
        "phone",
        "user",
        "is_approved",
        "is_active",
        "created_at",
    )

    list_display_links = (
        "id",
        "name",
    )

    search_fields = (
        "name",
        "company",
        "email",
        "phone",
        "user__username",
        "user__email",
    )

    list_filter = (
        "is_approved",
        "is_active",
        "created_at",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "approved_at",
    )

    autocomplete_fields = (
        "approved_by",
    )

    actions = (
        approve_suppliers,
        unapprove_suppliers,
        activate_suppliers,
        deactivate_suppliers,
    )

    fieldsets = (

        (
            "User Account",
            {
                "fields": (
                    "user",
                ),
            },
        ),

        (
            "Supplier Information",
            {
                "fields": (
                    "name",
                    "company",
                    "email",
                    "phone",
                    "address",
                ),
            },
        ),

        (
            "Business Information",
            {
                "fields": (
                    "business_license",
                    "tax_number",
                    "website",
                ),
            },
        ),

        (
            "Approval",
            {
                "fields": (
                    "is_approved",
                    "approved_at",
                    "approved_by",
                ),
            },
        ),

        (
            "Status",
            {
                "fields": (
                    "is_active",
                    "notes",
                ),
            },
        ),

        (
            "Timestamps",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
            },
        ),

    )