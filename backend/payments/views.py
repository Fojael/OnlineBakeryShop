from decimal import Decimal

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
# HELPER FUNCTIONS
# ==========================================================

def get_react_url(path):
    """
    Build React frontend URL.

    Example:
        FRONTEND_URL = "http://localhost:5173"

        get_react_url("payment/success/")
        ->
        http://localhost:5173/payment/success/
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
        value = request.GET.get(
            key,
            default,
        )

    return value


# ==========================================================
# VALIDATE SSLCommerz PAYMENT
# ==========================================================

def validate_sslcommerz_payment(
    payment,
    validation,
):
    """
    Validate SSLCommerz response against our Payment record.

    Checks:

    1. SSLCommerz status
    2. Transaction ID
    3. Payment amount
    4. Currency

    Returns:

        (True, "")

    on success.

        (False, error_message)

    on failure.
    """

    if not validation:
        return (
            False,
            "Empty validation response.",
        )

    # ------------------------------------------------------
    # Validate SSLCommerz status
    # ------------------------------------------------------

    validation_status = str(
        validation.get(
            "status",
            "",
        )
    ).upper()

    if validation_status != "VALID":
        return (
            False,
            "SSLCommerz validation failed.",
        )

    # ------------------------------------------------------
    # Validate transaction ID
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

    if returned_transaction_id != expected_transaction_id:
        return (
            False,
            "Transaction ID mismatch.",
        )

    # ------------------------------------------------------
    # Validate amount
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

    except (
        ValueError,
        TypeError,
    ):
        return (
            False,
            "Invalid payment amount.",
        )

    expected_amount = Decimal(
        str(
            payment.amount
        )
    )

    if returned_amount != expected_amount:
        return (
            False,
            "Payment amount mismatch.",
        )

    # ------------------------------------------------------
    # Validate currency
    # ------------------------------------------------------

    returned_currency = str(
        validation.get(
            "currency",
            "",
        )
    ).upper().strip()

    expected_currency = str(
        payment.currency
    ).upper().strip()

    if returned_currency != expected_currency:
        return (
            False,
            "Payment currency mismatch.",
        )

    return True, ""


# ==========================================================
# PROCESS SUCCESSFUL PAYMENT
# ==========================================================

def process_successful_payment(
    payment,
    validation,
):
    """
    Process a successfully validated SSLCommerz payment.

    This function:

    1. Locks the payment.
    2. Locks the order.
    3. Checks payment status.
    4. Checks product stock.
    5. Deducts stock.
    6. Marks payment as successful.
    7. Updates order status to Processing.
    8. Clears customer's cart.

    Everything is handled inside one database transaction.
    """

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
        # Prevent duplicate processing
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
        # Check stock again
        #
        # Stock may have changed while payment was pending.
        # --------------------------------------------------

        for item in order_items:

            product = item.product

            # Product must still be active
            if not product.is_active:
                raise ValueError(
                    f"{product.name} is no longer available."
                )

            # Current stock check
            if product.stock_quantity < item.quantity:
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

            product.stock_quantity -= item.quantity

            product.save(
                update_fields=[
                    "stock_quantity",
                ]
            )

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

        order.status = Order.STATUS_PROCESSING

        order.save(
            update_fields=[
                "status",
                "updated_at",
            ]
        )

        # --------------------------------------------------
        # Clear customer's cart
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

            # Cart may already have been deleted.
            pass

        return payment


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

    @transaction.atomic
    def post(
        self,
        request,
        order_id,
    ):

        # --------------------------------------------------
        # Get customer's order
        # --------------------------------------------------

        order = get_object_or_404(
            Order.objects.select_for_update(),
            id=order_id,
            customer=request.user,
        )

        # --------------------------------------------------
        # Only SSLCommerz orders can use this endpoint
        # --------------------------------------------------

        if (
            order.payment_method
            != Order.PAYMENT_SSLCOMMERZ
        ):

            return Response(
                {
                    "detail": (
                        "This order does not use "
                        "SSLCommerz payment."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # Prevent payment for cancelled order
        # --------------------------------------------------

        if order.status == Order.STATUS_CANCELLED:

            return Response(
                {
                    "detail": (
                        "Cancelled orders cannot "
                        "be paid."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # Validate order amount
        # --------------------------------------------------

        if order.total_amount is None:

            return Response(
                {
                    "detail": (
                        "Order amount is invalid."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        order_amount = Decimal(
            str(
                order.total_amount
            )
        )

        if order_amount <= 0:

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
        # Prevent duplicate successful payment
        # --------------------------------------------------

        if (
            payment
            and payment.status
            == Payment.STATUS_SUCCESS
        ):

            return Response(
                {
                    "detail": (
                        "This order has already "
                        "been paid."
                    ),
                    "order_id": order.id,
                    "payment_id": payment.id,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # Create SSLCommerz session
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

        except requests.RequestException as exc:

            return Response(
                {
                    "detail": (
                        "Unable to connect to "
                        "SSLCommerz."
                    ),
                    "error": str(exc),
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        except Exception as exc:

            return Response(
                {
                    "detail": (
                        "Unable to initialize "
                        "payment."
                    ),
                    "error": str(exc),
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # Validate gateway response
        # --------------------------------------------------

        gateway_status = str(
            gateway_response.get(
                "status",
                "",
            )
        ).upper()

        if gateway_status != "SUCCESS":

            return Response(
                {
                    "success": False,
                    "detail": gateway_response.get(
                        "failedreason",
                        "Unable to initialize payment.",
                    ),
                    "gateway_response": gateway_response,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # --------------------------------------------------
        # Get GatewayPageURL
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
                gateway=Payment.GATEWAY_SSLCOMMERZ,
                status=Payment.STATUS_PENDING,
            )

        else:

            # ------------------------------------------------
            # A failed/cancelled payment can be retried.
            # ------------------------------------------------

            payment.transaction_id = transaction_id

            payment.amount = (
                order.total_amount
            )

            payment.currency = "BDT"

            payment.gateway = (
                Payment.GATEWAY_SSLCOMMERZ
            )

            payment.status = (
                Payment.STATUS_PENDING
            )

            # Clear previous gateway information
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
        # Return payment information
        # --------------------------------------------------

        return Response(
            {
                "success": True,
                "message": (
                    "Payment session created successfully."
                ),
                "payment_url": gateway_page_url,
                "transaction_id": transaction_id,
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
# PAYMENT SUCCESS
# ==========================================================

@csrf_exempt
def payment_success(request):
    """
    SSLCommerz success callback.

    SSLCommerz sends:

        tran_id
        val_id

    The backend validates the transaction directly
    with SSLCommerz before completing the order.

    IMPORTANT:

    This endpoint redirects the customer's browser
    to the React PaymentSuccess page.

    It does NOT return JSON to the browser.
    """

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

        return redirect(
            get_react_url(
                "payment/failed/"
                "?reason=invalid_payment_response"
            )
        )

    # ------------------------------------------------------
    # Find payment
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

        return redirect(
            get_react_url(
                "payment/failed/"
                "?reason=payment_not_found"
            )
        )

    # ------------------------------------------------------
    # Already successful
    #
    # This prevents duplicate stock deduction.
    # ------------------------------------------------------

    if payment.status == Payment.STATUS_SUCCESS:

        return redirect(
            get_react_url(
                "payment/success/"
                f"?order_id={payment.order_id}"
                f"&payment_id={payment.id}"
                f"&transaction_id={payment.transaction_id}"
            )
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

        return redirect(
            get_react_url(
                "payment/failed/"
                f"?order_id={payment.order_id}"
                "&reason=gateway_validation_error"
            )
        )

    except Exception:

        return redirect(
            get_react_url(
                "payment/failed/"
                f"?order_id={payment.order_id}"
                "&reason=payment_validation_error"
            )
        )

    # ------------------------------------------------------
    # Validate payment data
    # ------------------------------------------------------

    is_valid, error_message = (
        validate_sslcommerz_payment(
            payment,
            validation,
        )
    )

    if not is_valid:

        payment.mark_failed()

        return redirect(
            get_react_url(
                "payment/failed/"
                f"?order_id={payment.order_id}"
                "&reason=validation_failed"
            )
        )

    # ------------------------------------------------------
    # Process payment
    # ------------------------------------------------------

    try:

        payment = process_successful_payment(
            payment,
            validation,
        )

    except ValueError:

        return redirect(
            get_react_url(
                "payment/failed/"
                f"?order_id={payment.order_id}"
                "&reason=order_processing_failed"
            )
        )

    except Exception:

        return redirect(
            get_react_url(
                "payment/failed/"
                f"?order_id={payment.order_id}"
                "&reason=payment_processing_failed"
            )
        )

    # ------------------------------------------------------
    # SUCCESS
    #
    # Browser is redirected to React.
    # ------------------------------------------------------

    return redirect(
        get_react_url(
            "payment/success/"
            f"?order_id={payment.order_id}"
            f"&payment_id={payment.id}"
            f"&transaction_id={payment.transaction_id}"
        )
    )


# ==========================================================
# PAYMENT FAILED
# ==========================================================

@csrf_exempt
def payment_fail(request):
    """
    SSLCommerz failed payment callback.

    This endpoint updates the Payment record and then
    redirects the customer's browser to React.
    """

    transaction_id = get_request_value(
        request,
        "tran_id",
    )

    order_id = None
    payment_id = None

    if transaction_id:

        try:

            payment = Payment.objects.get(
                transaction_id=transaction_id,
            )

            payment_id = payment.id
            order_id = payment.order_id

            # ----------------------------------------------
            # Never overwrite successful payment
            # ----------------------------------------------

            if (
                payment.status
                != Payment.STATUS_SUCCESS
            ):

                payment.mark_failed()

        except Payment.DoesNotExist:

            pass

    # ------------------------------------------------------
    # Build React URL
    # ------------------------------------------------------

    query_params = []

    if order_id:
        query_params.append(
            f"order_id={order_id}"
        )

    if payment_id:
        query_params.append(
            f"payment_id={payment_id}"
        )

    query_params.append(
        "reason=payment_failed"
    )

    query_string = "&".join(
        query_params
    )

    return redirect(
        get_react_url(
            f"payment/failed/?{query_string}"
        )
    )


# ==========================================================
# PAYMENT CANCELLED
# ==========================================================

@csrf_exempt
def payment_cancel(request):
    """
    SSLCommerz cancelled payment callback.

    This endpoint updates the Payment record and then
    redirects the customer's browser to React.
    """

    transaction_id = get_request_value(
        request,
        "tran_id",
    )

    order_id = None
    payment_id = None

    if transaction_id:

        try:

            payment = Payment.objects.get(
                transaction_id=transaction_id,
            )

            payment_id = payment.id
            order_id = payment.order_id

            # ----------------------------------------------
            # Never overwrite successful payment
            # ----------------------------------------------

            if (
                payment.status
                != Payment.STATUS_SUCCESS
            ):

                payment.mark_cancelled()

        except Payment.DoesNotExist:

            pass

    # ------------------------------------------------------
    # Build React URL
    # ------------------------------------------------------

    query_params = []

    if order_id:
        query_params.append(
            f"order_id={order_id}"
        )

    if payment_id:
        query_params.append(
            f"payment_id={payment_id}"
        )

    query_params.append(
        "reason=payment_cancelled"
    )

    query_string = "&".join(
        query_params
    )

    return redirect(
        get_react_url(
            f"payment/cancelled/?{query_string}"
        )
    )


# ==========================================================
# SSLCommerz IPN
# ==========================================================

@csrf_exempt
def payment_ipn(request):
    """
    SSLCommerz Instant Payment Notification.

    IPN is server-to-server.

    Therefore this endpoint DOES NOT redirect
    the browser.

    On successful validation:

        Payment -> Success
        Order   -> Processing
        Stock   -> Deducted
        Cart    -> Cleared
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
                "success": False,
                "detail": (
                    "Invalid IPN request."
                ),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ------------------------------------------------------
    # Find payment
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
                    "Payment already processed."
                ),
                "order_id": payment.order_id,
                "transaction_id": (
                    payment.transaction_id
                ),
                "status": payment.status,
            },
            status=status.HTTP_200_OK,
        )

    # ------------------------------------------------------
    # Validate payment with SSLCommerz
    # ------------------------------------------------------

    gateway = SSLCommerzGateway()

    try:

        validation = (
            gateway.validate_payment(
                validation_id
            )
        )

    except requests.RequestException as exc:

        return Response(
            {
                "success": False,
                "detail": (
                    "Unable to validate IPN "
                    "payment."
                ),
                "error": str(exc),
            },
            status=status.HTTP_502_BAD_GATEWAY,
        )

    except Exception as exc:

        return Response(
            {
                "success": False,
                "detail": (
                    "IPN validation error."
                ),
                "error": str(exc),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ------------------------------------------------------
    # Validate transaction
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

    try:

        payment = process_successful_payment(
            payment,
            validation,
        )

    except ValueError as exc:

        return Response(
            {
                "success": False,
                "detail": str(exc),
                "order_id": payment.order_id,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    except Exception as exc:

        return Response(
            {
                "success": False,
                "detail": (
                    "Unable to process IPN payment."
                ),
                "error": str(exc),
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    # ------------------------------------------------------
    # IPN success
    #
    # Keep this as JSON because IPN is server-to-server.
    # ------------------------------------------------------

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