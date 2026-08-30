from django.urls import path

from .views import (
    CreatePaymentView,
    PaymentStatusView,
    RetryPaymentView,
    SSLCommerzSuccessView,
    SSLCommerzFailView,
    SSLCommerzCancelView,
    SSLCommerzIPNView,
)


urlpatterns = [

    path(
        "orders/<int:order_id>/create/",
        CreatePaymentView.as_view(),
        name="create-payment",
    ),

    path(
        "orders/<int:order_id>/status/",
        PaymentStatusView.as_view(),
        name="payment-status",
    ),

    path(
        "orders/<int:order_id>/retry/",
        RetryPaymentView.as_view(),
        name="retry-payment",
    ),

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