from django.urls import path

from .views import (
    CreatePaymentView,
    payment_success,
    payment_fail,
    payment_cancel,
    payment_ipn,
)

app_name = "payments"

urlpatterns = [
    # ==========================================================
    # Create Payment Session
    # POST /api/payments/create/<order_id>/
    # ==========================================================
    path(
        "create/<int:order_id>/",
        CreatePaymentView.as_view(),
        name="create-payment",
    ),

    # ==========================================================
    # SSLCommerz Callback URLs
    # ==========================================================
    path(
        "success/",
        payment_success,
        name="payment-success",
    ),
    path(
        "fail/",
        payment_fail,
        name="payment-fail",
    ),
    path(
        "cancel/",
        payment_cancel,
        name="payment-cancel",
    ),
    path(
        "ipn/",
        payment_ipn,
        name="payment-ipn",
    ),
]