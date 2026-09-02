from uuid import uuid4
from decimal import Decimal

from django.db import transaction
from django.http import HttpResponseRedirect
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
from accounts.permissions import IsAdmin

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

    value = (
        f"BAKE"
        f"{order_id}"
        f"{uuid4().hex.upper()}"
    )

    return value[:30]


# ==========================================================
# CALLBACK VALUE
# ==========================================================

def _callback_value(request, key):

    value = (
        request.data.get(key)
        or request.query_params.get(key)
        or ""
    )

    return str(value).strip()


# ==========================================================
# CALLBACK TRANSACTION ID
# ==========================================================

def _callback_transaction_id(request):

    return _callback_value(
        request,
        "tran_id",
    )


# ==========================================================
# PAYMENT LOOKUP
# ==========================================================

def _get_payment_by_transaction(transaction_id):

    return get_object_or_404(
        Payment.objects.select_related(
            "order",
            "order__customer",
        ),
        transaction_id=transaction_id,
    )


# ==========================================================
# FINALIZE SUCCESS
# ==========================================================

@transaction.atomic
def finalize_success(payment, validation):

    # ======================================================
    # LOCK PAYMENT
    # ======================================================

    payment = (
        Payment.objects
        .select_for_update()
        .get(pk=payment.pk)
    )

    # ======================================================
    # LOCK ORDER
    # ======================================================

    order = (
        Order.objects
        .select_for_update()
        .get(pk=payment.order_id)
    )

    # ======================================================
    # IDEMPOTENCY
    # ======================================================

    if payment.status == Payment.STATUS_SUCCESS:

        return payment, False

    # ======================================================
    # CANCELLED ORDER
    # ======================================================

    if order.status == Order.STATUS_CANCELLED:

        raise SSLCommerzError(
            "This order has already been cancelled."
        )

    # ======================================================
    # TRANSACTION ID
    # ======================================================

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

    # ======================================================
    # CURRENCY
    # ======================================================

    returned_currency = str(
        validation.get("currency")
        or validation.get("currency_type")
        or ""
    ).upper()

    if returned_currency != payment.currency:

        raise SSLCommerzError(
            "Payment currency validation failed."
        )

    # ======================================================
    # AMOUNT
    # ======================================================

    try:

        returned_amount = Decimal(
            str(
                validation.get(
                    "amount",
                    "",
                )
            )
        )

    except (
        TypeError,
        ValueError,
    ) as exc:

        raise SSLCommerzError(
            "Payment amount validation failed."
        ) from exc

    expected_amount = Decimal(
        payment.amount
    )

    if returned_amount != expected_amount:

        raise SSLCommerzError(
            "Payment amount does not match the order."
        )

    # ======================================================
    # STATUS
    # ======================================================

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
            "SSLCommerz did not validate "
            "the transaction."
        )

    # ======================================================
    # RISK
    # ======================================================

    risk_level = str(
        validation.get(
            "risk_level",
            "0",
        )
    )

    if risk_level == "1":

        raise SSLCommerzError(
            "SSLCommerz marked this transaction as risky."
        )

    # ======================================================
    # ORDER ITEMS
    # ======================================================

    order_items = list(
        OrderItem.objects
        .select_related("product")
        .select_for_update()
        .filter(order=order)
    )

    if not order_items:

        raise SSLCommerzError(
            "This order contains no items."
        )

    # ======================================================
    # STOCK CHECK
    # ======================================================

    if not order.stock_deducted:

        for item in order_items:

            product = item.product

            if hasattr(product, "is_active"):

                if not product.is_active:

                    raise SSLCommerzError(
                        f"{product.name} is no longer available."
                    )

            if hasattr(product, "is_available"):

                if not product.is_available:

                    raise SSLCommerzError(
                        f"{product.name} is no longer available."
                    )

            if item.quantity <= 0:

                raise SSLCommerzError(
                    f"Invalid quantity for "
                    f"{product.name}."
                )

            if product.stock_quantity < item.quantity:

                raise SSLCommerzError(
                    f"Insufficient stock for "
                    f"{product.name}."
                )

        # ==================================================
        # DEDUCT STOCK
        # ==================================================

        for item in order_items:

            product = item.product

            product.stock_quantity -= item.quantity

            update_fields = [
                "stock_quantity",
            ]

            if hasattr(product, "is_available"):

                product.is_available = (
                    product.stock_quantity > 0
                )

                update_fields.append(
                    "is_available"
                )

            product.save(
                update_fields=update_fields
            )

        order.stock_deducted = True

    # ======================================================
    # REMOVE CART ITEMS
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

        for order_item in order_items:

            try:

                cart_item = (
                    CartItem.objects
                    .select_for_update()
                    .get(
                        cart=cart,
                        product=order_item.product,
                    )
                )

            except CartItem.DoesNotExist:

                continue

            if (
                cart_item.quantity
                <= order_item.quantity
            ):

                cart_item.delete()

            else:

                cart_item.quantity -= (
                    order_item.quantity
                )

                cart_item.save(
                    update_fields=[
                        "quantity",
                    ]
                )

    # ======================================================
    # PAYMENT
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
    # ORDER
    # ======================================================

    order.status = Order.STATUS_PROCESSING

    order.save(
        update_fields=[
            "status",
            "stock_deducted",
            "updated_at",
        ]
    )

    return payment, True


# ==========================================================
# FRONTEND REDIRECT HELPER
# ==========================================================

def _redirect(path, **params):

    return HttpResponseRedirect(
        frontend_redirect(
            path,
            **params,
        )
    )


# ==========================================================
# SUCCESS CALLBACK
# ==========================================================

@method_decorator(
    csrf_exempt,
    name="dispatch",
)
class SSLCommerzSuccessView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):

        return self._handle(request)

    def get(self, request):

        return self._handle(request)

    def _handle(self, request):

        transaction_id = (
            _callback_transaction_id(request)
        )

        if not transaction_id:

            return _redirect(
                "/payment/failed",
                reason="Transaction ID is missing.",
            )

        payment = None

        try:

            payment = (
                _get_payment_by_transaction(
                    transaction_id
                )
            )

            val_id = _callback_value(
                request,
                "val_id",
            )

            if not val_id:

                raise SSLCommerzError(
                    "Validation ID is missing."
                )

            validation = validate_transaction(
                val_id
            )

            payment, _ = finalize_success(
                payment,
                validation,
            )

            return _redirect(
                "/payment/success",
                order_id=payment.order_id,
                payment_id=payment.id,
                tran_id=payment.transaction_id,
            )

        except SSLCommerzError as exc:

            return _redirect(
                "/payment/failed",
                order_id=(
                    payment.order_id
                    if payment
                    else None
                ),
                tran_id=transaction_id,
                reason=str(exc),
            )


# ==========================================================
# FAILURE CALLBACK
# ==========================================================

@method_decorator(
    csrf_exempt,
    name="dispatch",
)
class SSLCommerzFailView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):

        return self._handle(request)

    def get(self, request):

        return self._handle(request)

    def _handle(self, request):

        transaction_id = (
            _callback_transaction_id(request)
        )

        if not transaction_id:

            return _redirect(
                "/payment/failed",
                reason="Payment transaction "
                       "was not identified.",
            )

        try:

            payment = (
                _get_payment_by_transaction(
                    transaction_id
                )
            )

        except Exception:

            return _redirect(
                "/payment/failed",
                tran_id=transaction_id,
                reason="Unknown transaction.",
            )

        with transaction.atomic():

            payment = (
                Payment.objects
                .select_for_update()
                .get(pk=payment.pk)
            )

            if (
                payment.status
                != Payment.STATUS_SUCCESS
            ):

                reason = (
                    _callback_value(
                        request,
                        "error",
                    )
                    or
                    _callback_value(
                        request,
                        "failedreason",
                    )
                    or
                    "SSLCommerz reported payment failure."
                )

                payment.mark_failed(reason)

                payment.gateway_response = dict(
                    request.data
                )

                payment.save(
                    update_fields=[
                        "status",
                        "failure_reason",
                        "gateway_response",
                        "updated_at",
                    ]
                )

        return _redirect(
            "/payment/failed",
            order_id=payment.order_id,
            tran_id=payment.transaction_id,
            reason=payment.failure_reason,
        )


# ==========================================================
# CANCEL CALLBACK
# ==========================================================

@method_decorator(
    csrf_exempt,
    name="dispatch",
)
class SSLCommerzCancelView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):

        return self._handle(request)

    def get(self, request):

        return self._handle(request)

    def _handle(self, request):

        transaction_id = (
            _callback_transaction_id(request)
        )

        if not transaction_id:

            return _redirect(
                "/payment/cancelled",
                reason="Transaction ID is missing.",
            )

        try:

            payment = (
                _get_payment_by_transaction(
                    transaction_id
                )
            )

        except Exception:

            return _redirect(
                "/payment/cancelled",
                tran_id=transaction_id,
                reason="Unknown transaction.",
            )

        with transaction.atomic():

            payment = (
                Payment.objects
                .select_for_update()
                .get(pk=payment.pk)
            )

            if (
                payment.status
                != Payment.STATUS_SUCCESS
            ):

                payment.mark_cancelled(
                    "Customer cancelled the payment."
                )

                payment.gateway_response = dict(
                    request.data
                )

                payment.save(
                    update_fields=[
                        "status",
                        "failure_reason",
                        "gateway_response",
                        "updated_at",
                    ]
                )

        return _redirect(
            "/payment/cancelled",
            order_id=payment.order_id,
            tran_id=payment.transaction_id,
        )


# ==========================================================
# IPN
# ==========================================================

@method_decorator(
    csrf_exempt,
    name="dispatch",
)
class SSLCommerzIPNView(APIView):

    authentication_classes = []
    permission_classes = []

    def post(self, request):

        transaction_id = (
            _callback_transaction_id(request)
        )

        if not transaction_id:

            return Response(
                {
                    "detail":
                        "Transaction ID is missing."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

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
                status=status.HTTP_404_NOT_FOUND,
            )

        gateway_status = str(
            request.data.get(
                "status",
                "",
            )
        ).upper()

        # ==================================================
        # SUCCESS
        # ==================================================

        if gateway_status in {
            "VALID",
            "VALIDATED",
        }:

            val_id = _callback_value(
                request,
                "val_id",
            )

            if not val_id:

                return Response(
                    {
                        "detail":
                            "Validation ID is missing."
                    },
                    status=(
                        status.HTTP_400_BAD_REQUEST
                    ),
                )

            try:

                validation = (
                    validate_transaction(
                        val_id
                    )
                )

                finalize_success(
                    payment,
                    validation,
                )

            except SSLCommerzError as exc:

                return Response(
                    {
                        "detail": str(exc)
                    },
                    status=(
                        status.HTTP_400_BAD_REQUEST
                    ),
                )

        # ==================================================
        # FAILED
        # ==================================================

        elif gateway_status in {
            "FAILED",
            "EXPIRED",
            "UNATTEMPTED",
            "CANCELLED",
        }:

            with transaction.atomic():

                payment = (
                    Payment.objects
                    .select_for_update()
                    .get(pk=payment.pk)
                )

                if (
                    payment.status
                    != Payment.STATUS_SUCCESS
                ):

                    if gateway_status == "CANCELLED":

                        payment.mark_cancelled(
                            "SSLCommerz cancelled "
                            "the payment."
                        )

                    elif gateway_status == "EXPIRED":

                        payment.mark_failed(
                            "SSLCommerz payment expired."
                        )

                    elif gateway_status == "UNATTEMPTED":

                        payment.mark_failed(
                            "No payment channel "
                            "was completed."
                        )

                    else:

                        payment.mark_failed(
                            "SSLCommerz reported "
                            "payment failure."
                        )

                    payment.gateway_response = dict(
                        request.data
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

            with transaction.atomic():

                payment = (
                    Payment.objects
                    .select_for_update()
                    .get(pk=payment.pk)
                )

                payment.gateway_response = dict(
                    request.data
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
# ADMIN PAYMENT MANAGEMENT
# ==========================================================

class AdminPaymentListView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]

    def get(self, request):
        payments = (
            Payment.objects
            .select_related(
                "order",
                "order__customer",
            )
            .order_by("-created_at")
        )

        return Response(
            {
                "count": payments.count(),
                "results": PaymentSerializer(payments, many=True).data,
            },
            status=status.HTTP_200_OK,
        )


class AdminPaymentStatusUpdateView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAdmin,
    ]

    def patch(self, request, payment_id):
        payment = get_object_or_404(
            Payment.objects.select_related("order"),
            pk=payment_id,
        )

        new_status = request.data.get("status")
        if new_status not in {
            Payment.STATUS_PENDING,
            Payment.STATUS_SUCCESS,
            Payment.STATUS_FAILED,
            Payment.STATUS_CANCELLED,
        }:
            return Response(
                {"detail": "Invalid payment status."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        payment.status = new_status
        if new_status == Payment.STATUS_SUCCESS:
            payment.mark_success()
            if payment.order.status not in {
                Order.STATUS_CANCELLED,
                Order.STATUS_DELIVERED,
            }:
                payment.order.status = Order.STATUS_PROCESSING
                payment.order.save(update_fields=["status", "updated_at"])
        elif new_status == Payment.STATUS_FAILED:
            payment.mark_failed(request.data.get("failure_reason", "Payment failed"))
        elif new_status == Payment.STATUS_CANCELLED:
            payment.mark_cancelled(request.data.get("failure_reason", "Payment cancelled"))
        else:
            payment.mark_pending()

        payment.save()

        return Response(
            {
                "message": "Payment status updated.",
                "payment": PaymentSerializer(payment).data,
            },
            status=status.HTTP_200_OK,
        )


# ==========================================================
# CREATE PAYMENT
# ==========================================================

class CreatePaymentView(APIView):

    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(self, request, order_id):

        # ==================================================
        # LOCK ORDER
        # ==================================================

        order = get_object_or_404(
            Order.objects.select_for_update(),
            id=order_id,
            customer=request.user,
        )

        # ==================================================
        # PAYMENT METHOD
        # ==================================================

        if (
            order.payment_method
            != Order.PAYMENT_SSLCOMMERZ
        ):

            return Response(
                {
                    "detail":
                        "This order does not "
                        "use SSLCommerz."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ==================================================
        # ORDER STATE
        # ==================================================

        if order.status in {
            Order.STATUS_CANCELLED,
            Order.STATUS_DELIVERED,
            Order.STATUS_PROCESSING,
        }:

            return Response(
                {
                    "detail":
                        "This order cannot be paid."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ==================================================
        # PAYMENT
        # ==================================================

        try:

            payment = (
                Payment.objects
                .select_for_update()
                .get(order=order)
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

        # ==================================================
        # ALREADY SUCCESS
        # ==================================================

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
        # NEW ATTEMPT
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
        # INITIATE
        # ==================================================

        try:

            gateway_response, gateway_url = (
                initiate_payment(
                    payment
                )
            )

        except SSLCommerzError as exc:

            payment.mark_failed(str(exc))

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
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # ==================================================
        # SAVE SESSION
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

    permission_classes = [
        IsAuthenticated,
    ]

    @transaction.atomic
    def post(self, request, order_id):

        order = get_object_or_404(
            Order.objects.select_for_update(),
            id=order_id,
            customer=request.user,
        )

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
                status=status.HTTP_400_BAD_REQUEST,
            )

        if order.status != Order.STATUS_PENDING:

            return Response(
                {
                    "detail":
                        "Only pending orders "
                        "can retry payment."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:

            payment = (
                Payment.objects
                .select_for_update()
                .get(order=order)
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

        try:

            gateway_response, gateway_url = (
                initiate_payment(
                    payment
                )
            )

        except SSLCommerzError as exc:

            payment.mark_failed(str(exc))

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
                status=status.HTTP_502_BAD_GATEWAY,
            )

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