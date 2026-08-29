# ==========================================================
# payments/views.py
# ==========================================================

from decimal import Decimal
from uuid import uuid4

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import Cart, CartItem
from orders.models import Order, OrderItem

from .models import Payment
from .serializers import PaymentSerializer
from .services import (
    SSLCommerzError,
    initiate_payment,
    validate_transaction,
)
from .utils import frontend_redirect


# ==========================================================
# TRANSACTION ID
# ==========================================================

def new_transaction_id(order_id):
    """
    Generate a unique SSLCommerz transaction ID.

    Maximum length:
        30 characters
    """

    value = f"BAKE{order_id}{uuid4().hex.upper()}"

    return value[:30]


# ==========================================================
# CALLBACK TRANSACTION ID
# ==========================================================

def _callback_transaction_id(request):
    """
    Read transaction ID from SSLCommerz callback.

    SSLCommerz can send the data through:
        POST body
        GET query parameters
    """

    return str(
        request.data.get("tran_id")
        or request.query_params.get("tran_id")
        or ""
    ).strip()


# ==========================================================
# GET PAYMENT BY TRANSACTION ID
# ==========================================================

def _get_payment_by_transaction(transaction_id):
    """
    Find payment using SSLCommerz transaction ID.
    """

    return get_object_or_404(
        Payment.objects.select_related(
            "order",
            "order__customer",
        ),
        transaction_id=transaction_id,
    )


# ==========================================================
# FINALIZE SUCCESSFUL PAYMENT
# ==========================================================

@transaction.atomic
def finalize_success(payment, validation):
    """
    Finalize a successfully validated SSLCommerz payment.

    This function performs the important server-side operations:

        1. Lock payment
        2. Lock order
        3. Validate transaction ID
        4. Validate currency
        5. Validate amount
        6. Validate SSLCommerz status
        7. Check risk level
        8. Lock order items
        9. Check stock
        10. Deduct stock
        11. Remove purchased products from cart
        12. Mark payment successful
        13. Store gateway information
        14. Set order to Processing

    It is protected by database transaction.atomic().
    """

    # ------------------------------------------------------
    # Lock payment
    # ------------------------------------------------------

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

    # ------------------------------------------------------
    # Lock order
    # ------------------------------------------------------

    order = (
        Order.objects
        .select_for_update()
        .get(
            pk=payment.order_id,
        )
    )

    # ------------------------------------------------------
    # Already successful
    #
    # Important for IPN + success callback.
    #
    # SSLCommerz may notify our backend more than once.
    # We must not deduct stock twice.
    # ------------------------------------------------------

    if payment.status == Payment.STATUS_SUCCESS:
        return payment, False

    # ------------------------------------------------------
    # Validate transaction ID
    # ------------------------------------------------------

    returned_tran_id = str(
        validation.get(
            "tran_id",
            "",
        )
    ).strip()

    if returned_tran_id != payment.transaction_id:

        raise SSLCommerzError(
            "Transaction ID validation failed."
        )

    # ------------------------------------------------------
    # Validate currency
    # ------------------------------------------------------

    returned_currency = str(
        validation.get("currency")
        or validation.get("currency_type")
        or ""
    ).upper()

    if returned_currency != payment.currency:

        raise SSLCommerzError(
            "Payment currency validation failed."
        )

    # ------------------------------------------------------
    # Validate amount
    # ------------------------------------------------------

    try:

        returned_amount = Decimal(
            str(
                validation.get(
                    "amount",
                )
            )
        )

    except (TypeError, ValueError):

        raise SSLCommerzError(
            "Payment amount validation failed."
        )

    if returned_amount != Decimal(
        payment.amount
    ):

        raise SSLCommerzError(
            "Payment amount does not match the order."
        )

    # ------------------------------------------------------
    # Validate SSLCommerz status
    # ------------------------------------------------------

    gateway_status = str(
        validation.get(
            "status",
            "",
        )
    ).upper()

    if gateway_status not in {
        "VALID",
        "VALIDATED",
    }:

        raise SSLCommerzError(
            "SSLCommerz did not validate the transaction."
        )

    # ------------------------------------------------------
    # Risk validation
    #
    # SSLCommerz risk_level:
    #     0 = normal
    #     1 = risky
    # ------------------------------------------------------

    if str(
        validation.get(
            "risk_level",
            "",
        )
    ) == "1":

        raise SSLCommerzError(
            "SSLCommerz marked this transaction as risky."
        )

    # ======================================================
    # GET AND LOCK ORDER ITEMS
    # ======================================================

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

        raise SSLCommerzError(
            "This order contains no items."
        )

    # ======================================================
    # CHECK PRODUCT STOCK
    # ======================================================

    for item in order_items:

        product = item.product

        # --------------------------------------------------
        # Product must still be active
        # --------------------------------------------------

        if not product.is_active:

            raise SSLCommerzError(
                f"{product.name} is no longer available."
            )

        # --------------------------------------------------
        # Quantity must be valid
        # --------------------------------------------------

        if item.quantity <= 0:

            raise SSLCommerzError(
                f"Invalid quantity for {product.name}."
            )

        # --------------------------------------------------
        # Check stock
        # --------------------------------------------------

        if (
            product.stock_quantity
            < item.quantity
        ):

            raise SSLCommerzError(
                f"Insufficient stock for "
                f"{product.name}."
            )

    # ======================================================
    # DEDUCT STOCK
    # ======================================================

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

    # ======================================================
    # REMOVE PURCHASED ITEMS FROM CART
    # ======================================================

    try:

        cart = (
            Cart.objects
            .select_for_update()
            .get(
                customer=order.customer,
            )
        )

    except Cart.DoesNotExist:

        cart = None

    if cart:

        for item in order_items:

            try:

                cart_item = (
                    CartItem.objects
                    .select_for_update()
                    .get(
                        cart=cart,
                        product=item.product,
                    )
                )

            except CartItem.DoesNotExist:

                continue

            # ------------------------------------------------
            # Remove item if cart quantity is fully purchased
            # ------------------------------------------------

            if (
                cart_item.quantity
                <= item.quantity
            ):

                cart_item.delete()

            # ------------------------------------------------
            # Otherwise reduce quantity
            # ------------------------------------------------

            else:

                cart_item.quantity -= (
                    item.quantity
                )

                cart_item.save(
                    update_fields=[
                        "quantity",
                    ]
                )

    # ======================================================
    # UPDATE PAYMENT
    # ======================================================

    payment.status = Payment.STATUS_SUCCESS

    payment.validation_id = str(
        validation.get(
            "val_id",
            "",
        )
    )[:100]

    payment.bank_transaction_id = str(
        validation.get(
            "bank_tran_id",
            "",
        )
    )[:100]

    payment.card_type = str(
        validation.get(
            "card_type",
            "",
        )
    )[:100]

    payment.card_brand = str(
        validation.get(
            "card_brand",
            "",
        )
    )[:50]

    payment.failure_reason = ""

    payment.gateway_response = validation

    payment.paid_at = timezone.now()

    payment.save(
        update_fields=[
            "status",
            "validation_id",
            "bank_transaction_id",
            "card_type",
            "card_brand",
            "failure_reason",
            "gateway_response",
            "paid_at",
            "updated_at",
        ]
    )

    # ======================================================
    # UPDATE ORDER
    # ======================================================

    order.status = Order.STATUS_PROCESSING

    order.save(
        update_fields=[
            "status",
            "updated_at",
        ]
    )

    return payment, True


# ==========================================================
# SSLCommerz SUCCESS
# ==========================================================

@method_decorator(
    csrf_exempt,
    name="dispatch",
)
class SSLCommerzSuccessView(APIView):

    """
    SSLCommerz success callback.

    Endpoint:

        POST /api/payments/sslcommerz/success/

    or:

        GET /api/payments/sslcommerz/success/

    SSLCommerz sends the customer here after successful payment.

    IMPORTANT:
        We DO NOT trust the callback alone.

        We call SSLCommerz validation API and validate:
            transaction ID
            amount
            currency
            status
            risk level
    """

    authentication_classes = []

    permission_classes = []

    def post(self, request):

        transaction_id = (
            _callback_transaction_id(
                request
            )
        )

        # --------------------------------------------------
        # Transaction ID required
        # --------------------------------------------------

        if not transaction_id:

            return Response(
                {
                    "detail":
                        "Transaction ID is missing."
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        payment = None

        try:

            # ----------------------------------------------
            # Find payment
            # ----------------------------------------------

            payment = (
                _get_payment_by_transaction(
                    transaction_id
                )
            )

            # ----------------------------------------------
            # Server-side validation with SSLCommerz
            # ----------------------------------------------

            validation = (
                validate_transaction(
                    request.data.get(
                        "val_id"
                    )
                )
            )

            # ----------------------------------------------
            # Finalize payment
            # ----------------------------------------------

            finalize_success(
                payment,
                validation,
            )

            # ----------------------------------------------
            # Redirect frontend
            # ----------------------------------------------

            return Response(
                status=status.HTTP_302_FOUND,
                headers={
                    "Location":
                        frontend_redirect(
                            "/payment/success",
                            order_id=payment.order_id,
                            payment_id=payment.id,
                            tran_id=(
                                payment.transaction_id
                            ),
                        )
                },
            )

        except SSLCommerzError as exc:

            return Response(
                status=status.HTTP_302_FOUND,
                headers={
                    "Location":
                        frontend_redirect(
                            "/payment/failed",
                            order_id=(
                                payment.order_id
                                if payment
                                else None
                            ),
                            tran_id=(
                                transaction_id
                            ),
                            reason=str(exc),
                        )
                },
            )

    def get(self, request):

        return self.post(request)


# ==========================================================
# SSLCommerz FAILURE
# ==========================================================

@method_decorator(
    csrf_exempt,
    name="dispatch",
)
class SSLCommerzFailView(APIView):

    """
    SSLCommerz failure callback.
    """

    authentication_classes = []

    permission_classes = []

    def post(self, request):

        return self._handle(request)

    def get(self, request):

        return self._handle(request)

    def _handle(self, request):

        transaction_id = (
            _callback_transaction_id(
                request
            )
        )

        # --------------------------------------------------
        # Missing transaction
        # --------------------------------------------------

        if not transaction_id:

            return Response(
                status=status.HTTP_302_FOUND,
                headers={
                    "Location":
                        frontend_redirect(
                            "/payment/failed",
                            reason=(
                                "Payment transaction "
                                "was not identified."
                            ),
                        )
                },
            )

        # --------------------------------------------------
        # Find payment
        # --------------------------------------------------

        payment = (
            _get_payment_by_transaction(
                transaction_id
            )
        )

        # --------------------------------------------------
        # Lock payment
        # --------------------------------------------------

        with transaction.atomic():

            payment = (
                Payment.objects
                .select_for_update()
                .get(
                    pk=payment.pk,
                )
            )

            # ----------------------------------------------
            # Never overwrite successful payment
            # ----------------------------------------------

            if (
                payment.status
                != Payment.STATUS_SUCCESS
            ):

                reason = (
                    request.data.get(
                        "error"
                    )
                    or
                    request.data.get(
                        "failedreason"
                    )
                    or
                    "SSLCommerz reported payment failure."
                )

                payment.mark_failed(
                    str(reason)
                )

                payment.gateway_response = (
                    dict(request.data)
                )

                payment.save(
                    update_fields=[
                        "status",
                        "failure_reason",
                        "gateway_response",
                        "updated_at",
                    ]
                )

        # --------------------------------------------------
        # Redirect frontend
        # --------------------------------------------------

        return Response(
            status=status.HTTP_302_FOUND,
            headers={
                "Location":
                    frontend_redirect(
                        "/payment/failed",
                        order_id=payment.order_id,
                        tran_id=(
                            payment.transaction_id
                        ),
                        reason=(
                            payment.failure_reason
                        ),
                    )
            },
        )


# ==========================================================
# SSLCommerz CANCEL
# ==========================================================

@method_decorator(
    csrf_exempt,
    name="dispatch",
)
class SSLCommerzCancelView(APIView):

    """
    SSLCommerz cancellation callback.
    """

    authentication_classes = []

    permission_classes = []

    def post(self, request):

        return self._handle(request)

    def get(self, request):

        return self._handle(request)

    def _handle(self, request):

        transaction_id = (
            _callback_transaction_id(
                request
            )
        )

        # --------------------------------------------------
        # Missing transaction
        # --------------------------------------------------

        if not transaction_id:

            return Response(
                status=status.HTTP_302_FOUND,
                headers={
                    "Location":
                        frontend_redirect(
                            "/payment/cancelled",
                            reason=(
                                "Payment transaction "
                                "was not identified."
                            ),
                        )
                },
            )

        # --------------------------------------------------
        # Find payment
        # --------------------------------------------------

        payment = (
            _get_payment_by_transaction(
                transaction_id
            )
        )

        # --------------------------------------------------
        # Lock payment
        # --------------------------------------------------

        with transaction.atomic():

            payment = (
                Payment.objects
                .select_for_update()
                .get(
                    pk=payment.pk,
                )
            )

            # ----------------------------------------------
            # Never change successful payment
            # ----------------------------------------------

            if (
                payment.status
                != Payment.STATUS_SUCCESS
            ):

                payment.mark_cancelled(
                    "Customer cancelled the payment."
                )

                payment.gateway_response = (
                    dict(request.data)
                )

                payment.save(
                    update_fields=[
                        "status",
                        "failure_reason",
                        "gateway_response",
                        "updated_at",
                    ]
                )

        # --------------------------------------------------
        # Redirect frontend
        # --------------------------------------------------

        return Response(
            status=status.HTTP_302_FOUND,
            headers={
                "Location":
                    frontend_redirect(
                        "/payment/cancelled",
                        order_id=payment.order_id,
                        tran_id=(
                            payment.transaction_id
                        ),
                    )
            },
        )


# ==========================================================
# SSLCommerz IPN
# ==========================================================

@method_decorator(
    csrf_exempt,
    name="dispatch",
)
class SSLCommerzIPNView(APIView):

    """
    SSLCommerz Instant Payment Notification.

    This endpoint is server-to-server.

    It is extremely important because the browser callback
    should NOT be treated as the final source of truth.

    IPN flow:

        SSLCommerz
             |
             v
        Django IPN
             |
             v
        Validate transaction
             |
             v
        Update Payment
             |
             v
        Update Order
    """

    authentication_classes = []

    permission_classes = []

    def post(self, request):

        transaction_id = (
            _callback_transaction_id(
                request
            )
        )

        # --------------------------------------------------
        # Transaction ID required
        # --------------------------------------------------

        if not transaction_id:

            return Response(
                {
                    "detail":
                        "Transaction ID is missing."
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        # --------------------------------------------------
        # Find payment
        # --------------------------------------------------

        try:

            payment = (
                _get_payment_by_transaction(
                    transaction_id
                )
            )

        except Exception:

            return Response(
                {
                    "detail":
                        "Unknown transaction."
                },
                status=(
                    status.HTTP_404_NOT_FOUND
                ),
            )

        # --------------------------------------------------
        # Gateway status
        # --------------------------------------------------

        gateway_status = str(
            request.data.get(
                "status",
                "",
            )
        ).upper()

        # ==================================================
        # SUCCESSFUL IPN
        # ==================================================

        if gateway_status in {
            "VALID",
            "VALIDATED",
        }:

            try:

                # ------------------------------------------
                # Validate directly with SSLCommerz
                # ------------------------------------------

                validation = (
                    validate_transaction(
                        request.data.get(
                            "val_id"
                        )
                    )
                )

                # ------------------------------------------
                # Finalize payment
                # ------------------------------------------

                finalize_success(
                    payment,
                    validation,
                )

            except SSLCommerzError as exc:

                return Response(
                    {
                        "detail":
                            str(exc)
                    },
                    status=(
                        status.HTTP_400_BAD_REQUEST
                    ),
                )

        # ==================================================
        # FAILED / CANCELLED IPN
        # ==================================================

        elif gateway_status in {
            "FAILED",
            "CANCELLED",
            "EXPIRED",
            "UNATTEMPTED",
        }:

            with transaction.atomic():

                payment = (
                    Payment.objects
                    .select_for_update()
                    .get(
                        pk=payment.pk,
                    )
                )

                # ------------------------------------------
                # Never overwrite successful payment
                # ------------------------------------------

                if (
                    payment.status
                    != Payment.STATUS_SUCCESS
                ):

                    if gateway_status == "CANCELLED":

                        payment.mark_cancelled(
                            "SSLCommerz cancelled the payment."
                        )

                    elif gateway_status == "EXPIRED":

                        payment.mark_failed(
                            "SSLCommerz payment expired."
                        )

                    elif gateway_status == "UNATTEMPTED":

                        payment.mark_failed(
                            "No payment channel was completed."
                        )

                    else:

                        payment.mark_failed(
                            "SSLCommerz reported payment failure."
                        )

                    payment.gateway_response = (
                        dict(request.data)
                    )

                    payment.save(
                        update_fields=[
                            "status",
                            "failure_reason",
                            "gateway_response",
                            "updated_at",
                        ]
                    )

        # ==================================================
        # UNKNOWN STATUS
        # ==================================================

        else:

            # Store unknown callback for debugging/audit.
            with transaction.atomic():

                payment = (
                    Payment.objects
                    .select_for_update()
                    .get(
                        pk=payment.pk,
                    )
                )

                payment.gateway_response = (
                    dict(request.data)
                )

                payment.save(
                    update_fields=[
                        "gateway_response",
                        "updated_at",
                    ]
                )

        return Response(
            {
                "message":
                    "IPN received."
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# CREATE PAYMENT
# ==========================================================

class CreatePaymentView(APIView):

    """
    Create an SSLCommerz payment session.

    Endpoint:

        POST /api/payments/create/<order_id>/

    Authentication:
        Required.

    Customer can only create payment for their own order.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(self, request, order_id):

        # --------------------------------------------------
        # Lock order
        # --------------------------------------------------

        order = get_object_or_404(
            Order.objects.select_for_update(),
            id=order_id,
            customer=request.user,
        )

        # --------------------------------------------------
        # Only SSLCommerz orders
        # --------------------------------------------------

        if (
            order.payment_method
            != Order.PAYMENT_SSLCOMMERZ
        ):

            return Response(
                {
                    "detail": (
                        "This order does not "
                        "use SSLCommerz."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        # --------------------------------------------------
        # Cancelled/delivered orders cannot be paid
        # --------------------------------------------------

        if order.status in {
            Order.STATUS_CANCELLED,
            Order.STATUS_DELIVERED,
        }:

            return Response(
                {
                    "detail":
                        "This order cannot be paid."
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        # ==================================================
        # GET OR CREATE PAYMENT
        # ==================================================

        try:

            payment = (
                Payment.objects
                .select_for_update()
                .get(
                    order=order,
                )
            )

        except Payment.DoesNotExist:

            payment = Payment.objects.create(
                order=order,
                transaction_id=(
                    new_transaction_id(
                        order.id
                    )
                ),
                amount=order.total_amount,
                currency="BDT",
            )

        # --------------------------------------------------
        # Already paid
        # --------------------------------------------------

        if (
            payment.status
            == Payment.STATUS_SUCCESS
        ):

            return Response(
                {
                    "message":
                        "Order is already paid.",
                    "payment":
                        PaymentSerializer(
                            payment
                        ).data,
                },
                status=status.HTTP_200_OK,
            )

        # ==================================================
        # NEW PAYMENT ATTEMPT
        # ==================================================

        payment.transaction_id = (
            new_transaction_id(
                order.id
            )
        )

        payment.amount = (
            order.total_amount
        )

        payment.currency = "BDT"

        payment.attempt_count += 1

        payment.mark_pending()

        payment.save()

        # ==================================================
        # CREATE SSLCommerz SESSION
        # ==================================================

        try:

            gateway_response, gateway_url = (
                initiate_payment(
                    payment
                )
            )

        except SSLCommerzError as exc:

            payment.mark_failed(
                str(exc)
            )

            payment.save(
                update_fields=[
                    "status",
                    "failure_reason",
                    "updated_at",
                ]
            )

            return Response(
                {
                    "detail":
                        str(exc)
                },
                status=(
                    status.HTTP_502_BAD_GATEWAY
                ),
            )

        # ==================================================
        # SAVE GATEWAY SESSION
        # ==================================================

        payment.session_key = str(
            gateway_response.get(
                "sessionkey",
                "",
            )
        )[:100]

        payment.gateway_response = (
            gateway_response
        )

        payment.save(
            update_fields=[
                "session_key",
                "gateway_response",
                "updated_at",
            ]
        )

        # ==================================================
        # RESPONSE
        # ==================================================

        return Response(
            {
                "message":
                    "Payment session created.",

                "gateway_url":
                    gateway_url,

                "payment":
                    PaymentSerializer(
                        payment
                    ).data,
            },
            status=status.HTTP_201_CREATED,
        )


# ==========================================================
# PAYMENT STATUS
# ==========================================================

class PaymentStatusView(APIView):

    """
    Get payment status for customer's order.

    Endpoint:

        GET /api/payments/status/<order_id>/

    Authentication:
        Required.
    """

    permission_classes = [
        IsAuthenticated,
    ]

    def get(self, request, order_id):

        payment = get_object_or_404(
            Payment.objects.select_related(
                "order",
            ),
            order__id=order_id,
            order__customer=request.user,
        )

        return Response(
            PaymentSerializer(
                payment
            ).data,
            status=status.HTTP_200_OK,
        )


# ==========================================================
# RETRY PAYMENT
# ==========================================================

class RetryPaymentView(APIView):

    """
    Create a new SSLCommerz payment attempt.

    Endpoint:

        POST /api/payments/retry/<order_id>/

    Retry is allowed when:

        Order = Pending

    Retry is NOT allowed when:

        Order = Processing
        Order = Delivered
        Order = Cancelled
    """

    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(self, request, order_id):

        # --------------------------------------------------
        # Lock order
        # --------------------------------------------------

        order = get_object_or_404(
            Order.objects.select_for_update(),
            id=order_id,
            customer=request.user,
        )

        # --------------------------------------------------
        # Only SSLCommerz
        # --------------------------------------------------

        if (
            order.payment_method
            != Order.PAYMENT_SSLCOMMERZ
        ):

            return Response(
                {
                    "detail":
                        "Retry is available only "
                        "for SSLCommerz."
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        # --------------------------------------------------
        # Retry only pending orders
        # --------------------------------------------------

        if (
            order.status
            != Order.STATUS_PENDING
        ):

            return Response(
                {
                    "detail": (
                        "Only pending orders "
                        "can retry payment."
                    )
                },
                status=(
                    status.HTTP_400_BAD_REQUEST
                ),
            )

        # ==================================================
        # GET OR CREATE PAYMENT
        # ==================================================

        try:

            payment = (
                Payment.objects
                .select_for_update()
                .get(
                    order=order,
                )
            )

        except Payment.DoesNotExist:

            payment = Payment.objects.create(
                order=order,
                transaction_id=(
                    new_transaction_id(
                        order.id
                    )
                ),
                amount=order.total_amount,
                currency="BDT",
            )

        # --------------------------------------------------
        # Already paid
        # --------------------------------------------------

        if (
            payment.status
            == Payment.STATUS_SUCCESS
        ):

            return Response(
                {
                    "message":
                        "Order is already paid.",

                    "payment":
                        PaymentSerializer(
                            payment
                        ).data,
                },
                status=status.HTTP_200_OK,
            )

        # ==================================================
        # CREATE NEW PAYMENT ATTEMPT
        # ==================================================

        payment.transaction_id = (
            new_transaction_id(
                order.id
            )
        )

        payment.amount = (
            order.total_amount
        )

        payment.currency = "BDT"

        payment.attempt_count += 1

        payment.mark_pending()

        payment.save()

        # ==================================================
        # CREATE NEW SSLCommerz SESSION
        # ==================================================

        try:

            gateway_response, gateway_url = (
                initiate_payment(
                    payment
                )
            )

        except SSLCommerzError as exc:

            payment.mark_failed(
                str(exc)
            )

            payment.save(
                update_fields=[
                    "status",
                    "failure_reason",
                    "updated_at",
                ]
            )

            return Response(
                {
                    "detail":
                        str(exc)
                },
                status=(
                    status.HTTP_502_BAD_GATEWAY
                ),
            )

        # ==================================================
        # SAVE SESSION INFORMATION
        # ==================================================

        payment.session_key = str(
            gateway_response.get(
                "sessionkey",
                "",
            )
        )[:100]

        payment.gateway_response = (
            gateway_response
        )

        payment.save(
            update_fields=[
                "session_key",
                "gateway_response",
                "updated_at",
            ]
        )

        # ==================================================
        # RESPONSE
        # ==================================================

        return Response(
            {
                "message":
                    "New payment attempt created.",

                "gateway_url":
                    gateway_url,

                "payment":
                    PaymentSerializer(
                        payment
                    ).data,
            },
            status=status.HTTP_201_CREATED,
        )