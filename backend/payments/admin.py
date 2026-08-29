# ==========================================================
# payments/admin.py
# ==========================================================

from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    # ======================================================
    # LIST DISPLAY
    # ======================================================

    list_display = (
        "id",
        "order",
        "transaction_id",
        "amount",
        "currency",
        "status",
        "attempt_count",
        "paid_at",
        "created_at",
    )

    # ======================================================
    # FILTERS
    # ======================================================

    list_filter = (
        "status",
        "currency",
        "created_at",
        "paid_at",
    )

    # ======================================================
    # SEARCH
    # ======================================================

    search_fields = (
        "transaction_id",
        "validation_id",
        "bank_transaction_id",
        "order__id",
        "order__customer__username",
        "order__customer__email",
    )

    # ======================================================
    # READ ONLY FIELDS
    # ======================================================

    readonly_fields = (
        "transaction_id",
        "validation_id",
        "bank_transaction_id",
        "session_key",
        "gateway_response",
        "created_at",
        "updated_at",
        "paid_at",
    )

    # ======================================================
    # DEFAULT ORDERING
    # ======================================================

    ordering = (
        "-created_at",
    )

    # ======================================================
    # DATE HIERARCHY
    # ======================================================

    date_hierarchy = "created_at"

    # ======================================================
    # ITEMS PER PAGE
    # ======================================================

    list_per_page = 25