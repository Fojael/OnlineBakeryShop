from decimal import Decimal, InvalidOperation
from urllib.parse import urlencode

import requests

from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import Cart, CartItem
from orders.models import Order, OrderItem

from .models import Payment
from .services import SSLCommerzGateway


# ==========================================================
# FRONTEND URL
# ==========================================================

def get_react_url(path):

    base_url = getattr(
        settings,
        "FRONTEND_URL",
        "http://localhost:5173",
    )

    return (
        f"{base_url.rstrip('/')}/"
        f"{path.lstrip('/')}"
    )


# ==========================================================
# REQUEST VALUE
# ==========================================================

def get_request_value(
    request,
    key,
    default="",
):

    value = request.POST.get(key)

    if value is None:

        value = request.GET.get(
            key,
            default,
        )

    return value


# ==========================================================
# REDIRECT REACT
# ==========================================================

def redirect_to_react(
    path,
    params=None,
):

    if params:

        clean_params = {
            key: value
            for key, value in params.items()
            if value is not None
            and value != ""
        }

        if clean_params:

            query_string = urlencode(
                clean_params
            )

            path = (
                f"{path.rstrip('/')}/"
                f"?{query_string}"
            )

    return redirect(
        get_react_url(path)
    )


# ==========================================================
# VALIDATE PAYMENT
# ==========================================================

def validate_sslcommerz_payment(
    payment,
    validation,
):

    if not validation:

        return (
            False,
            "Empty validation response.",
        )

    # ------------------------------------------------------
    # Status
    # ------------------------------------------------------

    validation_status = str(
        validation.get(
            "status",
            "",
        )
    ).upper().strip()

    if validation_status not in {
        "VALID",
        "VALIDATED",
    }:

        return (
            False,
            (
                "SSLCommerz transaction "
                f"status is "
                f"{validation_status or 'unknown'}."
            ),
        )

    # ------------------------------------------------------
    # Transaction ID
    # ------------------------------------------------------

    returned_transaction_id = str(
        validation.get(
            "tran_id",
            "",
        )
    ).strip()

    expected_transaction_id = str(
        payment.transaction_id
    ).strip()

    if (
        not returned_transaction_id
        or returned_transaction_id
        != expected_transaction_id
    ):

        return (
            False,
            "Transaction ID does not match.",
        )

    # ------------------------------------------------------
    # Amount
    # ------------------------------------------------------

    try:

        returned_amount = Decimal(
            str(
                validation.get(
                    "amount",
                    "0",
                )
            )
        )

        expected_amount = Decimal(
            str(payment.amount)
        )

    except (
        ValueError,
        TypeError,
        InvalidOperation,
    ):

        return (
            False,
            "Invalid payment amount.",
        )

    if returned_amount != expected_amount:

        return (
            False,
            "Payment amount does not match.",
        )

    # ------------------------------------------------------
    # Currency
    # ------------------------------------------------------

    returned_currency = str(
        validation.get(
            "currency",
            validation.get(
                "currency_type",
                "",
            ),
        )
    ).upper().strip()

    expected_currency = str(
        payment.currency
    ).upper().strip()

    if (
        not returned_currency
        or returned_currency
        != expected_currency
    ):

        return (
            False,
            "Payment currency does not match.",
        )

    return True, ""


# ==========================================================
# PROCESS SUCCESSFUL PAYMENT
# ==========================================================

def process_successful_payment(
    payment,
    validation,
):

    with transaction.atomic():

        # --------------------------------------------------
        # Lock payment
        # --------------------------------------------------

        payment = (
            Payment.objects
            .select_for_update()
            .select_related(
                "order",
                "order__customer",
            )
            .get(
                pk=payment.pk,
            )
        )

        # --------------------------------------------------
        # Idempotency
        # --------------------------------------------------

        if payment.status == Payment.STATUS_SUCCESS:

            return payment

        # --------------------------------------------------
        # Lock order
        # --------------------------------------------------

        order = (
            Order.objects
            .select_for_update()
            .get(
                pk=payment.order_id,
            )
        )

        # --------------------------------------------------
        # Cancelled order
        # --------------------------------------------------

        if (
            order.status
            == Order.STATUS_CANCELLED
        ):

            raise ValueError(
                "This order has been cancelled."
            )

        # --------------------------------------------------
        # Get order items
        # --------------------------------------------------

        order_items = list(
            OrderItem.objects
            .select_related(
                "product",
            )
            .select_for_update()
            .filter(
                order=order,
            )
        )

        if not order_items:

            raise ValueError(
                "Order does not contain any items."
            )

        # --------------------------------------------------
        # Validate stock
        # --------------------------------------------------

        for item in order_items:

            product = item.product

            if not product.is_active:

                raise ValueError(
                    f"{product.name} "
                    "is no longer available."
                )

            if (
                product.stock_quantity
                < item.quantity
            ):

                raise ValueError(
                    f"Insufficient stock for "
                    f"{product.name}. "
                    f"Available: "
                    f"{product.stock_quantity}, "
                    f"Required: "
                    f"{item.quantity}."
                )

        # --------------------------------------------------
        # Deduct stock
        # --------------------------------------------------

        for item in order_items:

            product = item.product

            product.stock_quantity -= (
                item.quantity
            )

            product.save(
                update_fields=[
                    "stock_quantity",
                ]
            )

        # --------------------------------------------------
        # Mark payment success
        # --------------------------------------------------

        payment.mark_success(

            gateway_transaction_id=(
                validation.get(
                    "tran_id",
                    "",
                )
            ),

            bank_transaction_id=(
                validation.get(
                    "bank_tran_id",
                    "",
                )
            ),

            validation_id=(
                validation.get(
                    "val_id",
                    "",
                )
            ),

            card_type=(
                validation.get(
                    "card_type",
                    "",
                )
            ),

            card_brand=(
                validation.get(
                    "card_brand",
                    "",
                )
            ),

            card_issuer=(
                validation.get(
                    "card_issuer",
                    "",
                )
            ),
        )

        # --------------------------------------------------
        # Update order
        # --------------------------------------------------

        order.status = (
            Order.STATUS_PROCESSING
        )

        order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        # --------------------------------------------------
        # Clear cart
        # --------------------------------------------------

        try:

            cart = (
                Cart.objects
                .select_for_update()
                .get(
                    customer=order.customer,
                )
            )

            CartItem.objects.filter(
                cart=cart,
            ).delete()

        except Cart.DoesNotExist:

            pass

        return payment


# ==========================================================
# CREATE PAYMENT
# ==========================================================

class CreatePaymentView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(
        self,
        request,
        order_id,
    ):

        # --------------------------------------------------
        # Get order
        # --------------------------------------------------

        order = get_object_or_404(
            Order.objects.select_for_update(),
            id=order_id,
            customer=request.user,
        )

        # --------------------------------------------------
        # Payment method
        # --------------------------------------------------

        if (
            order.payment_method
            != Order.PAYMENT_SSLCOMMERZ
        ):

            return Response(
                {
                    "success": False,
                    "detail": (
                        "This order does not use "
                        "SSLCommerz payment."
                    ),
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        # --------------------------------------------------
        # Cancelled
        # --------------------------------------------------

        if (
            order.status
            == Order.STATUS_CANCELLED
        ):

            return Response(
                {
                    "success": False,
                    "detail": (
                        "Cancelled orders cannot "
                        "be paid."
                    ),
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        # --------------------------------------------------
        # Amount
        # --------------------------------------------------

        if order.total_amount is None:

            return Response(
                {
                    "success": False,
                    "detail": (
                        "Order amount is invalid."
                    ),
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        try:

            order_amount = Decimal(
                str(order.total_amount)
            )

        except (
            ValueError,
            TypeError,
            InvalidOperation,
        ):

            return Response(
                {
                    "success": False,
                    "detail": (
                        "Order amount is invalid."
                    ),
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        if order_amount <= 0:

            return Response(
                {
                    "success": False,
                    "detail": (
                        "Order amount must be "
                        "greater than zero."
                    ),
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        # --------------------------------------------------
        # Existing payment
        # --------------------------------------------------

        try:

            payment = order.payment

        except Payment.DoesNotExist:

            payment = None

        # --------------------------------------------------
        # Already paid
        # --------------------------------------------------

        if (
            payment
            and payment.status
            == Payment.STATUS_SUCCESS
        ):

            return Response(
                {
                    "success": False,
                    "detail": (
                        "This order has already "
                        "been paid."
                    ),
                    "order_id": order.id,
                    "payment_id": payment.id,
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        # --------------------------------------------------
        # Create gateway session
        # --------------------------------------------------

        gateway = SSLCommerzGateway()

        try:

            (
                transaction_id,
                gateway_response,
            ) = gateway.create_session(
                order=order,
                customer=request.user,
            )

        except requests.RequestException:

            return Response(
                {
                    "success": False,
                    "detail": (
                        "Unable to connect to "
                        "SSLCommerz."
                    ),
                },
                status=(
                    status.HTTP_502_BAD_GATEWAY
                ),
            )

        except ValueError as exc:

            return Response(
                {
                    "success": False,
                    "detail": str(exc),
                },
                status=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
            )

        except Exception:

            return Response(
                {
                    "success": False,
                    "detail": (
                        "Unable to initialize "
                        "payment."
                    ),
                },
                status=(
                    status.HTTP_500_INTERNAL_SERVER_ERROR
                ),
            )

        # --------------------------------------------------
        # Gateway status
        # --------------------------------------------------

        gateway_status = str(
            gateway_response.get(
                "status",
                "",
            )
        ).upper().strip()

        if gateway_status != "SUCCESS":

            return Response(
                {
                    "success": False,
                    "detail": (
                        gateway_response.get(
                            "failedreason",
                            "Unable to initialize payment.",
                        )
                    ),
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        # --------------------------------------------------
        # Gateway URL
        # --------------------------------------------------

        gateway_page_url = (
            gateway_response.get(
                "GatewayPageURL"
            )
            or gateway_response.get(
                "gatewayPageURL"
            )
            or gateway_response.get(
                "gateway_page_url"
            )
        )

        if not gateway_page_url:

            return Response(
                {
                    "success": False,
                    "detail": (
                        "SSLCommerz did not return "
                        "a payment URL."
                    ),
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        # --------------------------------------------------
        # Create / update payment
        # --------------------------------------------------

        if payment is None:

            payment = Payment.objects.create(

                order=order,

                transaction_id=(
                    transaction_id
                ),

                amount=order_amount,

                currency="BDT",

                gateway=(
                    Payment.GATEWAY_SSLCOMMERZ
                ),

                status=(
                    Payment.STATUS_PENDING
                ),
            )

        else:

            payment.transaction_id = (
                transaction_id
            )

            payment.amount = (
                order_amount
            )

            payment.currency = "BDT"

            payment.gateway = (
                Payment.GATEWAY_SSLCOMMERZ
            )

            payment.status = (
                Payment.STATUS_PENDING
            )

            payment.gateway_transaction_id = ""
            payment.bank_transaction_id = ""
            payment.validation_id = ""

            payment.card_type = ""
            payment.card_brand = ""
            payment.card_issuer = ""

            payment.paid_at = None

            payment.save(
                update_fields=[
                    "transaction_id",
                    "amount",
                    "currency",
                    "gateway",
                    "status",

                    "gateway_transaction_id",
                    "bank_transaction_id",
                    "validation_id",

                    "card_type",
                    "card_brand",
                    "card_issuer",

                    "paid_at",
                    "updated_at",
                ]
            )

        # --------------------------------------------------
        # Response
        # --------------------------------------------------

        return Response(
            {
                "success": True,

                "message": (
                    "Payment session created "
                    "successfully."
                ),

                "payment_url": (
                    gateway_page_url
                ),

                "transaction_id": (
                    payment.transaction_id
                ),

                "payment_id": payment.id,

                "order_id": order.id,

                "amount": str(
                    payment.amount
                ),

                "currency": payment.currency,
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# SUCCESS CALLBACK
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

    if (
        not validation_id
        or not transaction_id
    ):

        return redirect_to_react(
            "payment/failed/",
            {
                "reason": (
                    "invalid_payment_response"
                ),
            },
        )

    try:

        payment = (
            Payment.objects
            .select_related(
                "order",
                "order__customer",
            )
            .get(
                transaction_id=transaction_id,
            )
        )

    except Payment.DoesNotExist:

        return redirect_to_react(
            "payment/failed/",
            {
                "reason": (
                    "payment_not_found"
                ),
            },
        )

    # ------------------------------------------------------
    # Already successful
    # ------------------------------------------------------

    if (
        payment.status
        == Payment.STATUS_SUCCESS
    ):

        return redirect_to_react(
            "payment/success/",
            {
                "order_id": payment.order_id,
                "payment_id": payment.id,
                "transaction_id": (
                    payment.transaction_id
                ),
            },
        )

    # ------------------------------------------------------
    # Validate
    # ------------------------------------------------------

    gateway = SSLCommerzGateway()

    try:

        validation = (
            gateway.validate_payment(
                validation_id
            )
        )

    except requests.RequestException:

        return redirect_to_react(
            "payment/failed/",
            {
                "order_id": payment.order_id,
                "payment_id": payment.id,
                "reason": (
                    "gateway_validation_error"
                ),
            },
        )

    except Exception:

        return redirect_to_react(
            "payment/failed/",
            {
                "order_id": payment.order_id,
                "payment_id": payment.id,
                "reason": (
                    "payment_validation_error"
                ),
            },
        )

    # ------------------------------------------------------
    # Validate response
    # ------------------------------------------------------

    is_valid, error_message = (
        validate_sslcommerz_payment(
            payment,
            validation,
        )
    )

    if not is_valid:

        payment.mark_failed()

        return redirect_to_react(
            "payment/failed/",
            {
                "order_id": payment.order_id,
                "payment_id": payment.id,
                "reason": (
                    "validation_failed"
                ),
            },
        )

    # ------------------------------------------------------
    # Process
    # ------------------------------------------------------

    try:

        payment = (
            process_successful_payment(
                payment,
                validation,
            )
        )

    except ValueError:

        return redirect_to_react(
            "payment/failed/",
            {
                "order_id": payment.order_id,
                "payment_id": payment.id,
                "reason": (
                    "order_processing_failed"
                ),
            },
        )

    except Exception:

        return redirect_to_react(
            "payment/failed/",
            {
                "order_id": payment.order_id,
                "payment_id": payment.id,
                "reason": (
                    "payment_processing_failed"
                ),
            },
        )

    return redirect_to_react(
        "payment/success/",
        {
            "order_id": payment.order_id,
            "payment_id": payment.id,
            "transaction_id": (
                payment.transaction_id
            ),
        },
    )


# ==========================================================
# FAIL CALLBACK
# ==========================================================

@csrf_exempt
def payment_fail(request):

    transaction_id = get_request_value(
        request,
        "tran_id",
    )

    order_id = None
    payment_id = None

    if transaction_id:

        try:

            payment = (
                Payment.objects.get(
                    transaction_id=transaction_id
                )
            )

            order_id = payment.order_id
            payment_id = payment.id

            payment.mark_failed()

        except Payment.DoesNotExist:

            pass

    return redirect_to_react(
        "payment/failed/",
        {
            "order_id": order_id,
            "payment_id": payment_id,
            "reason": "payment_failed",
        },
    )


# ==========================================================
# CANCEL CALLBACK
# ==========================================================

@csrf_exempt
def payment_cancel(request):

    transaction_id = get_request_value(
        request,
        "tran_id",
    )

    order_id = None
    payment_id = None

    if transaction_id:

        try:

            payment = (
                Payment.objects.get(
                    transaction_id=transaction_id
                )
            )

            order_id = payment.order_id
            payment_id = payment.id

            payment.mark_cancelled()

        except Payment.DoesNotExist:

            pass

    return redirect_to_react(
        "payment/cancelled/",
        {
            "order_id": order_id,
            "payment_id": payment_id,
            "reason": "payment_cancelled",
        },
    )


# ==========================================================
# IPN
# ==========================================================

@csrf_exempt
def payment_ipn(request):

    transaction_id = get_request_value(
        request,
        "tran_id",
    )

    validation_id = get_request_value(
        request,
        "val_id",
    )

    # ------------------------------------------------------
    # Required fields
    # ------------------------------------------------------

    if (
        not transaction_id
        or not validation_id
    ):

        return Response(
            {
                "success": False,
                "detail": (
                    "Invalid IPN request."
                ),
            },
            status=(
                status.HTTP_400_BAD_REQUEST
            ),
        )

    # ------------------------------------------------------
    # Payment
    # ------------------------------------------------------

    try:

        payment = (
            Payment.objects
            .select_related(
                "order",
                "order__customer",
            )
            .get(
                transaction_id=transaction_id,
            )
        )

    except Payment.DoesNotExist:

        return Response(
            {
                "success": False,
                "detail": (
                    "Payment transaction "
                    "not found."
                ),
            },
            status=(
                status.HTTP_404_NOT_FOUND
            ),
        )

    # ------------------------------------------------------
    # Idempotency
    # ------------------------------------------------------

    if (
        payment.status
        == Payment.STATUS_SUCCESS
    ):

        return Response(
            {
                "success": True,
                "message": (
                    "Payment already processed."
                ),
                "order_id": payment.order_id,
                "transaction_id": (
                    payment.transaction_id
                ),
                "payment_id": payment.id,
                "status": payment.status,
            },
            status=status.HTTP_200_OK,
        )

    # ------------------------------------------------------
    # Validate with SSLCommerz
    # ------------------------------------------------------

    gateway = SSLCommerzGateway()

    try:

        validation = (
            gateway.validate_payment(
                validation_id
            )
        )

    except requests.RequestException:

        return Response(
            {
                "success": False,
                "detail": (
                    "Unable to validate "
                    "IPN payment."
                ),
            },
            status=(
                status.HTTP_502_BAD_GATEWAY
            ),
        )

    except Exception:

        return Response(
            {
                "success": False,
                "detail": (
                    "IPN validation error."
                ),
            },
            status=(
                status.HTTP_400_BAD_REQUEST
            ),
        )

    # ------------------------------------------------------
    # Validate
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
            status=(
                status.HTTP_400_BAD_REQUEST
            ),
        )

    # ------------------------------------------------------
    # Process
    # ------------------------------------------------------

    try:

        payment = (
            process_successful_payment(
                payment,
                validation,
            )
        )

    except ValueError as exc:

        return Response(
            {
                "success": False,
                "detail": str(exc),
                "order_id": payment.order_id,
            },
            status=(
                status.HTTP_400_BAD_REQUEST
            ),
        )

    except Exception:

        return Response(
            {
                "success": False,
                "detail": (
                    "Unable to process "
                    "IPN payment."
                ),
            },
            status=(
                status.HTTP_500_INTERNAL_SERVER_ERROR
            ),
        )

    return Response(
        {
            "success": True,
            "message": (
                "IPN processed successfully."
            ),
            "order_id": payment.order_id,
            "transaction_id": (
                payment.transaction_id
            ),
            "payment_id": payment.id,
            "status": payment.status,
        },
        status=status.HTTP_200_OK,
    )