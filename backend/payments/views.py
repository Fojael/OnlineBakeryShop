# payments/views.py

from decimal import Decimal

import requests

from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from orders.models import Order

from .models import Payment
from .services import SSLCommerzGateway


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def get_react_url(path):
    """
    Build React frontend URL.
    """

    base_url = getattr(
        settings,
        "FRONTEND_URL",
        "http://localhost:5173",
    )

    return f"{base_url.rstrip('/')}/{path.lstrip('/')}"


def get_request_value(request, key, default=""):
    """
    Read a value from POST or GET.

    SSLCommerz normally sends callback data through POST,
    but GET is accepted as a fallback for local testing.
    """

    value = request.POST.get(key)

    if value is None:
        value = request.GET.get(key, default)

    return value


def validate_sslcommerz_payment(payment, validation):
    """
    Validate SSLCommerz response against our Payment record.

    Returns:
        (True, "") on success
        (False, error_message) on failure
    """

    if not validation:
        return False, "Empty validation response."

    # ------------------------------------------------------
    # Validate SSLCommerz status
    # ------------------------------------------------------

    validation_status = str(
        validation.get("status", "")
    ).upper()

    if validation_status != "VALID":
        return False, "SSLCommerz validation failed."

    # ------------------------------------------------------
    # Validate transaction ID
    # ------------------------------------------------------

    returned_transaction_id = str(
        validation.get("tran_id", "")
    )

    if returned_transaction_id != payment.transaction_id:
        return False, "Transaction ID mismatch."

    # ------------------------------------------------------
    # Validate amount
    # ------------------------------------------------------

    try:
        returned_amount = Decimal(
            str(validation.get("amount", "0"))
        )
    except (ValueError, TypeError):
        return False, "Invalid payment amount."

    expected_amount = Decimal(
        str(payment.amount)
    )

    if returned_amount != expected_amount:
        return False, "Payment amount mismatch."

    # ------------------------------------------------------
    # Validate currency
    # ------------------------------------------------------

    returned_currency = str(
        validation.get("currency", "")
    ).upper()

    expected_currency = str(
        payment.currency
    ).upper()

    if returned_currency != expected_currency:
        return False, "Payment currency mismatch."

    return True, ""


def process_successful_payment(payment, validation):
    """
    Mark payment and order as successful.

    Both payment and order are updated inside
    a database transaction.
    """

    with transaction.atomic():

        # --------------------------------------------------
        # Prevent duplicate processing
        # --------------------------------------------------

        if payment.status == Payment.STATUS_SUCCESS:
            return

        # --------------------------------------------------
        # Mark payment successful
        # --------------------------------------------------

        payment.mark_success(
            gateway_transaction_id=validation.get(
                "tran_id",
                "",
            ),
            bank_transaction_id=validation.get(
                "bank_tran_id",
                "",
            ),
            validation_id=validation.get(
                "val_id",
                "",
            ),
            card_type=validation.get(
                "card_type",
                "",
            ),
            card_brand=validation.get(
                "card_brand",
                "",
            ),
            card_issuer=validation.get(
                "card_issuer",
                "",
            ),
        )

        # --------------------------------------------------
        # Update order status
        # --------------------------------------------------

        order = payment.order

        order.status = Order.STATUS_PROCESSING

        order.save(
            update_fields=[
                "status",
            ]
        )


# ==========================================================
# CREATE PAYMENT SESSION
# ==========================================================

class CreatePaymentView(APIView):
    """
    Create SSLCommerz payment session.

    POST:
        /api/payments/create/<order_id>/
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def post(self, request, order_id):

        # --------------------------------------------------
        # Find customer's order
        # --------------------------------------------------

        order = get_object_or_404(
            Order,
            id=order_id,
            customer=request.user,
        )

        # --------------------------------------------------
        # Validate order amount
        # --------------------------------------------------

        if order.total_amount is None:

            return Response(
                {
                    "detail": "Order amount is invalid."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if Decimal(str(order.total_amount)) <= 0:

            return Response(
                {
                    "detail": (
                        "Order amount must be "
                        "greater than zero."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # Check existing payment
        # --------------------------------------------------

        try:

            payment = order.payment

        except Payment.DoesNotExist:

            payment = None

        # --------------------------------------------------
        # Prevent duplicate payment
        # --------------------------------------------------

        if (
            payment
            and payment.status == Payment.STATUS_SUCCESS
        ):

            return Response(
                {
                    "detail": (
                        "This order has already been paid."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # Create SSLCommerz session
        # --------------------------------------------------

        gateway = SSLCommerzGateway()

        try:

            transaction_id, gateway_response = (
                gateway.create_session(
                    order=order,
                    customer=request.user,
                )
            )

        except requests.RequestException as exc:

            return Response(
                {
                    "detail": (
                        "Unable to connect to SSLCommerz."
                    ),
                    "error": str(exc),
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        except Exception as exc:

            return Response(
                {
                    "detail": (
                        "Unable to initialize payment."
                    ),
                    "error": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # Validate gateway response
        # --------------------------------------------------

        if gateway_response.get("status") != "SUCCESS":

            return Response(
                {
                    "detail": gateway_response.get(
                        "failedreason",
                        "Unable to initialize payment.",
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        gateway_page_url = gateway_response.get(
            "GatewayPageURL"
        )

        if not gateway_page_url:

            return Response(
                {
                    "detail": (
                        "SSLCommerz did not return "
                        "a payment URL."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # Create or update Payment
        # --------------------------------------------------

        if payment is None:

            payment = Payment.objects.create(
                order=order,
                transaction_id=transaction_id,
                amount=order.total_amount,
                currency="BDT",
                status=Payment.STATUS_PENDING,
            )

        else:

            payment.transaction_id = transaction_id
            payment.amount = order.total_amount
            payment.currency = "BDT"
            payment.status = Payment.STATUS_PENDING

            payment.save(
                update_fields=[
                    "transaction_id",
                    "amount",
                    "currency",
                    "status",
                    "updated_at",
                ]
            )

        # --------------------------------------------------
        # Return payment URL
        # --------------------------------------------------

        return Response(
            {
                "success": True,
                "payment_url": gateway_page_url,
                "transaction_id": transaction_id,
                "payment_id": payment.id,
                "order_id": order.id,
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# PAYMENT SUCCESS
# ==========================================================

@csrf_exempt
def payment_success(request):

    validation_id = get_request_value(
        request,
        "val_id",
    )

    transaction_id = get_request_value(
        request,
        "tran_id",
    )

    # ------------------------------------------------------
    # Validate callback data
    # ------------------------------------------------------

    if not validation_id or not transaction_id:

        return Response(
            {
                "detail": "Invalid payment response."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ------------------------------------------------------
    # Find payment
    # ------------------------------------------------------

    try:

        payment = Payment.objects.get(
            transaction_id=transaction_id
        )

    except Payment.DoesNotExist:

        return Response(
            {
                "detail": (
                    "Payment transaction not found."
                )
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    # ------------------------------------------------------
    # Prevent duplicate processing
    # ------------------------------------------------------

    if payment.status == Payment.STATUS_SUCCESS:

        return Response(
            {
                "success": True,
                "message": (
                    "Payment has already been completed."
                ),
                "order_id": payment.order_id,
                "redirect_url": get_react_url(
                    f"payment/success/"
                    f"?order_id={payment.order_id}"
                ),
            },
            status=status.HTTP_200_OK,
        )

    # ------------------------------------------------------
    # Validate payment with SSLCommerz
    # ------------------------------------------------------

    gateway = SSLCommerzGateway()

    try:

        validation = gateway.validate_payment(
            validation_id
        )

    except requests.RequestException as exc:

        return Response(
            {
                "detail": (
                    "Unable to validate payment "
                    "with SSLCommerz."
                ),
                "error": str(exc),
            },
            status=status.HTTP_502_BAD_GATEWAY,
        )

    except Exception as exc:

        return Response(
            {
                "detail": "Payment validation error.",
                "error": str(exc),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ------------------------------------------------------
    # Validate payment
    # ------------------------------------------------------

    is_valid, error_message = (
        validate_sslcommerz_payment(
            payment,
            validation,
        )
    )

    if not is_valid:

        payment.mark_failed()

        return Response(
            {
                "success": False,
                "detail": error_message,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ------------------------------------------------------
    # Process successful payment
    # ------------------------------------------------------

    process_successful_payment(
        payment,
        validation,
    )

    # ------------------------------------------------------
    # Return success response
    # ------------------------------------------------------

    return Response(
        {
            "success": True,
            "message": (
                "Payment completed successfully."
            ),
            "order_id": payment.order_id,
            "transaction_id": payment.transaction_id,
            "status": payment.status,
            "redirect_url": get_react_url(
                f"payment/success/"
                f"?order_id={payment.order_id}"
            ),
        },
        status=status.HTTP_200_OK,
    )


# ==========================================================
# PAYMENT FAILED
# ==========================================================

@csrf_exempt
def payment_fail(request):

    transaction_id = get_request_value(
        request,
        "tran_id",
    )

    order_id = None

    if transaction_id:

        try:

            payment = Payment.objects.get(
                transaction_id=transaction_id
            )

            # Do not overwrite successful payment
            if payment.status != Payment.STATUS_SUCCESS:

                payment.mark_failed()

            order_id = payment.order_id

        except Payment.DoesNotExist:

            pass

    return Response(
        {
            "success": False,
            "message": "Payment failed.",
            "order_id": order_id,
            "redirect_url": get_react_url(
                "payment/failed/"
            ),
        },
        status=status.HTTP_200_OK,
    )


# ==========================================================
# PAYMENT CANCELLED
# ==========================================================

@csrf_exempt
def payment_cancel(request):

    transaction_id = get_request_value(
        request,
        "tran_id",
    )

    order_id = None

    if transaction_id:

        try:

            payment = Payment.objects.get(
                transaction_id=transaction_id
            )

            # Do not overwrite successful payment
            if payment.status != Payment.STATUS_SUCCESS:

                payment.mark_cancelled()

            order_id = payment.order_id

        except Payment.DoesNotExist:

            pass

    return Response(
        {
            "success": False,
            "message": "Payment cancelled.",
            "order_id": order_id,
            "redirect_url": get_react_url(
                "payment/cancelled/"
            ),
        },
        status=status.HTTP_200_OK,
    )


# ==========================================================
# SSLCommerz IPN
# ==========================================================

@csrf_exempt
def payment_ipn(request):
    """
    SSLCommerz Instant Payment Notification.

    The IPN callback validates the transaction directly
    with SSLCommerz before marking the payment successful.
    """

    transaction_id = get_request_value(
        request,
        "tran_id",
    )

    validation_id = get_request_value(
        request,
        "val_id",
    )

    # ------------------------------------------------------
    # Validate IPN data
    # ------------------------------------------------------

    if not transaction_id or not validation_id:

        return Response(
            {
                "detail": "Invalid IPN request."
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ------------------------------------------------------
    # Find payment
    # ------------------------------------------------------

    try:

        payment = Payment.objects.get(
            transaction_id=transaction_id
        )

    except Payment.DoesNotExist:

        return Response(
            {
                "detail": (
                    "Payment transaction not found."
                )
            },
            status=status.HTTP_404_NOT_FOUND,
        )

    # ------------------------------------------------------
    # Prevent duplicate processing
    # ------------------------------------------------------

    if payment.status == Payment.STATUS_SUCCESS:

        return Response(
            {
                "success": True,
                "message": "Payment already processed.",
                "order_id": payment.order_id,
                "transaction_id": payment.transaction_id,
            },
            status=status.HTTP_200_OK,
        )

    # ------------------------------------------------------
    # Validate payment through SSLCommerz
    # ------------------------------------------------------

    gateway = SSLCommerzGateway()

    try:

        validation = gateway.validate_payment(
            validation_id
        )

    except requests.RequestException as exc:

        return Response(
            {
                "detail": (
                    "Unable to validate IPN payment."
                ),
                "error": str(exc),
            },
            status=status.HTTP_502_BAD_GATEWAY,
        )

    except Exception as exc:

        return Response(
            {
                "detail": "IPN validation error.",
                "error": str(exc),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ------------------------------------------------------
    # Validate transaction data
    # ------------------------------------------------------

    is_valid, error_message = (
        validate_sslcommerz_payment(
            payment,
            validation,
        )
    )

    if not is_valid:

        payment.mark_failed()

        return Response(
            {
                "success": False,
                "detail": error_message,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ------------------------------------------------------
    # Process successful payment
    # ------------------------------------------------------

    process_successful_payment(
        payment,
        validation,
    )

    return Response(
        {
            "success": True,
            "message": "IPN processed successfully.",
            "order_id": payment.order_id,
            "transaction_id": payment.transaction_id,
        },
        status=status.HTTP_200_OK,
    )