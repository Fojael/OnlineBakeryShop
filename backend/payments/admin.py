from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "order",
        "transaction_id",
        "gateway",
        "amount",
        "currency",
        "status",
        "paid_at",
        "created_at",
    )

    list_filter = (
        "gateway",
        "status",
        "currency",
        "created_at",
        "paid_at",
    )

    search_fields = (
        "transaction_id",
        "gateway_transaction_id",
        "bank_transaction_id",
        "validation_id",
        "order__id",
        "order__customer__username",
        "order__customer__email",
    )

    ordering = (
        "-created_at",
    )

    readonly_fields = (
        "transaction_id",
        "gateway_transaction_id",
        "bank_transaction_id",
        "validation_id",
        "card_type",
        "card_brand",
        "card_issuer",
        "paid_at",
        "created_at",
        "updated_at",
    )

    fieldsets = (
        (
            "Payment Information",
            {
                "fields": (
                    "order",
                    "gateway",
                    "status",
                    "amount",
                    "currency",
                )
            },
        ),
        (
            "Transaction Details",
            {
                "fields": (
                    "transaction_id",
                    "gateway_transaction_id",
                    "bank_transaction_id",
                    "validation_id",
                )
            },
        ),
        (
            "Card Information",
            {
                "fields": (
                    "card_type",
                    "card_brand",
                    "card_issuer",
                )
            },
        ),
        (
            "Timestamps",
            {
                "fields": (
                    "paid_at",
                    "created_at",
                    "updated_at",
                )
            },
        ),
    )