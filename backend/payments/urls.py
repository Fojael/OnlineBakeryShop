from django.urls import path

from .views import (
    CreatePaymentView,
    PaymentStatusView,
    RetryPaymentView,
    SSLCommerzCancelView,
    SSLCommerzFailView,
    SSLCommerzIPNView,
    SSLCommerzSuccessView,
)


app_name = "payments"


urlpatterns = [

    # ======================================================
    # PAYMENT
    # ======================================================

    path(
        "create/<int:order_id>/",
        CreatePaymentView.as_view(),
        name="create-payment",
    ),

    path(
        "status/<int:order_id>/",
        PaymentStatusView.as_view(),
        name="payment-status",
    ),

    path(
        "retry/<int:order_id>/",
        RetryPaymentView.as_view(),
        name="retry-payment",
    ),

    # ======================================================
    # SSL COMMERZ
    # ======================================================

    path(
        "sslcommerz/success/",
        SSLCommerzSuccessView.as_view(),
        name="sslcommerz-success",
    ),

    path(
        "sslcommerz/fail/",
        SSLCommerzFailView.as_view(),
        name="sslcommerz-fail",
    ),

    path(
        "sslcommerz/cancel/",
        SSLCommerzCancelView.as_view(),
        name="sslcommerz-cancel",
    ),

    path(
        "sslcommerz/ipn/",
        SSLCommerzIPNView.as_view(),
        name="sslcommerz-ipn",
    ),
]