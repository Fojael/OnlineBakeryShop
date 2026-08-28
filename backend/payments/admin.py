from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = [
        "id",
        "order",
        "transaction_id",
        "gateway",
        "amount",
        "currency",
        "status",
        "paid_at",
        "created_at",
    ]

    list_filter = [
        "status",
        "gateway",
        "currency",
        "created_at",
    ]

    search_fields = [
        "transaction_id",
        "gateway_transaction_id",
        "bank_transaction_id",
        "validation_id",
        "order__id",
    ]

    readonly_fields = [
        "transaction_id",
        "gateway_transaction_id",
        "bank_transaction_id",
        "validation_id",
        "paid_at",
        "created_at",
        "updated_at",
    ]

    ordering = [
        "-created_at",
    ]