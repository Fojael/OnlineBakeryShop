from django.urls import path

from .views import (
    CreatePaymentView,
    payment_success,
    payment_fail,
    payment_cancel,
    payment_ipn,
)


urlpatterns = [

    # ======================================================
    # CREATE PAYMENT
    # ======================================================

    path(
        "payments/create/<int:order_id>/",
        CreatePaymentView.as_view(),
        name="create-payment",
    ),

    # ======================================================
    # SSLCommerz CALLBACKS
    # ======================================================

    path(
        "payments/success/",
        payment_success,
        name="payment-success",
    ),

    path(
        "payments/fail/",
        payment_fail,
        name="payment-fail",
    ),

    path(
        "payments/cancel/",
        payment_cancel,
        name="payment-cancel",
    ),

    # ======================================================
    # IPN
    # ======================================================

    path(
        "payments/ipn/",
        payment_ipn,
        name="payment-ipn",
    ),
]