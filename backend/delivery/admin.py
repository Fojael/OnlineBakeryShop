from django.contrib import admin

from .models import Delivery


@admin.register(Delivery)
class DeliveryAdmin(
    admin.ModelAdmin
):

    list_display = [
        "id",
        "order",
        "rider",
        "status",
        "assigned_at",
        "accepted_at",
        "delivered_at",
        "created_at",
    ]

    list_filter = [
        "status",
        "created_at",
    ]

    search_fields = [
        "order__id",
        "order__customer__email",
        "rider__email",
        "rider__username",
    ]

    readonly_fields = [
        "assigned_at",
        "accepted_at",
        "picked_up_at",
        "out_for_delivery_at",
        "delivered_at",
        "created_at",
        "updated_at",
    ]
    
