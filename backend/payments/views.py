from itertools import product
from uuid import uuid4
from decimal import Decimal

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

    value = (
        f"BAKE"
        f"{order_id}"
        f"{uuid4().hex.upper()}"
    )

    return value[:30]


# ==========================================================
# CALLBACK VALUE
# ==========================================================

def _callback_value(
    request,
    key,
):

    value = (
        request.data.get(key)
        or
        request.query_params.get(key)
        or
        ""
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
# PAYMENT BY TRANSACTION
# ==========================================================

def _get_payment_by_transaction(
    transaction_id,
):

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
def finalize_success(
    payment,
    validation,
):

    # ======================================================
    # LOCK PAYMENT
    # ======================================================

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

    # ======================================================
    # LOCK ORDER
    # ======================================================

    order = (
        Order.objects
        .select_for_update()
        .get(
            pk=payment.order_id,
        )
    )

    # ======================================================
    # ALREADY SUCCESSFUL
    #
    # This prevents duplicate stock deduction.
    # ======================================================

    if (
        payment.status
        == Payment.STATUS_SUCCESS
    ):

        return payment, False

    # ======================================================
    # ORDER MUST NOT BE CANCELLED
    # ======================================================

    if (
        order.status
        == Order.STATUS_CANCELLED
    ):

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

    if (
        returned_tran_id
        != payment.transaction_id
    ):

        raise SSLCommerzError(
            "Transaction ID validation failed."
        )

    # ======================================================
    # CURRENCY
    # ======================================================

    returned_currency = str(
        validation.get("currency")
        or
        validation.get("currency_type")
        or
        ""
    ).upper()

    if (
        returned_currency
        != payment.currency
    ):

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
    ):

        raise SSLCommerzError(
            "Payment amount validation failed."
        )

    if (
        returned_amount
        != Decimal(payment.amount)
    ):

        raise SSLCommerzError(
            "Payment amount does not match the order."
        )

    # ======================================================
    # SSL COMMERZ STATUS
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
            "SSLCommerz did not validate the transaction."
        )

    # ======================================================
    # RISK
    # ======================================================

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
    # ORDER ITEMS
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
    # CHECK STOCK
    # ======================================================

    for item in order_items:

        product = item.product

        # --------------------------------------------------
        # Product active/available
        # --------------------------------------------------

        if hasattr(
            product,
            "is_active",
        ):

            if not product.is_active:

                raise SSLCommerzError(
                    f"{product.name} is no longer available."
                )

        if hasattr(
            product,
            "is_available",
        ):

            if not product.is_available:

                raise SSLCommerzError(
                    f"{product.name} is no longer available."
                )

        # --------------------------------------------------
        # Quantity
        # --------------------------------------------------

        if item.quantity <= 0:

            raise SSLCommerzError(
                f"Invalid quantity for {product.name}."
            )

        # --------------------------------------------------
        # Stock
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

    if not order.stock_deducted:

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
    # REMOVE PURCHASED CART ITEMS
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
            # Fully purchased
            # ------------------------------------------------

            if (
                cart_item.quantity
                <= item.quantity
            ):

                cart_item.delete()

            # ------------------------------------------------
            # Partially purchased
            # ------------------------------------------------

            else:

                cart_item.quantity -= (
                    item.quantity
                )

                cart_item.save(
                    update_fields=[
                        "quantity",
                    ],
                )

    # ======================================================
    # UPDATE PAYMENT
    # ======================================================

    payment.status = (
        Payment.STATUS_SUCCESS
    )

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
        ],
    )

    # ======================================================
    # UPDATE ORDER
    # ======================================================

    order.status = (
        Order.STATUS_PROCESSING
    )

    order.save(
        update_fields=[
            "status",
            "stock_deducted",
            "updated_at",
        ],
    )

    return payment, True


# ==========================================================
# SSL COMMERZ SUCCESS
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
            _callback_transaction_id(
                request
            )
        )

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

            # ------------------------------------------------
            # Find payment
            # ------------------------------------------------

            payment = (
                _get_payment_by_transaction(
                    transaction_id
                )
            )

            # ------------------------------------------------
            # Validation ID
            #
            # Supports both POST and GET.
            # ------------------------------------------------

            val_id = _callback_value(
                request,
                "val_id",
            )

            if not val_id:

                raise SSLCommerzError(
                    "Validation ID is missing."
                )

            # ------------------------------------------------
            # Validate with SSLCommerz
            # ------------------------------------------------

            validation = (
                validate_transaction(
                    val_id
                )
            )

            # ------------------------------------------------
            # Finalize
            # ------------------------------------------------

            finalize_success(
                payment,
                validation,
            )

            # ------------------------------------------------
            # Frontend
            # ------------------------------------------------

            return Response(
                status=status.HTTP_302_FOUND,
                headers={
                    "Location":
                        frontend_redirect(
                            "/payment/success",
                            order_id=(
                                payment.order_id
                            ),
                            payment_id=(
                                payment.id
                            ),
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


# ==========================================================
# SSL COMMERZ FAILURE
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
            _callback_transaction_id(
                request
            )
        )

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

        payment = (
            _get_payment_by_transaction(
                transaction_id
            )
        )

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

                payment.mark_failed(
                    reason
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
                    ],
                )

        return Response(
            status=status.HTTP_302_FOUND,
            headers={
                "Location":
                    frontend_redirect(
                        "/payment/failed",
                        order_id=(
                            payment.order_id
                        ),
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
# SSL COMMERZ CANCEL
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
            _callback_transaction_id(
                request
            )
        )

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

        payment = (
            _get_payment_by_transaction(
                transaction_id
            )
        )

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

                payment.gateway_response = dict(
                    request.data
                )

                payment.save(
                    update_fields=[
                        "status",
                        "failure_reason",
                        "gateway_response",
                        "updated_at",
                    ],
                )

        return Response(
            status=status.HTTP_302_FOUND,
            headers={
                "Location":
                    frontend_redirect(
                        "/payment/cancelled",
                        order_id=(
                            payment.order_id
                        ),
                        tran_id=(
                            payment.transaction_id
                        ),
                    )
            },
        )


# ==========================================================
# SSL COMMERZ IPN
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
            _callback_transaction_id(
                request
            )
        )

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
        # SUCCESS
        # ==================================================

        if gateway_status in {
            "VALID",
            "VALIDATED",
        }:

            try:

                val_id = _callback_value(
                    request,
                    "val_id",
                )

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
                        "detail":
                            str(exc)
                    },
                    status=(
                        status.HTTP_400_BAD_REQUEST
                    ),
                )

        # ==================================================
        # FAILED / CANCELLED
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

                # ------------------------------------------------
                # Never overwrite successful payment
                # ------------------------------------------------

                if (
                    payment.status
                    != Payment.STATUS_SUCCESS
                ):

                    if (
                        gateway_status
                        == "CANCELLED"
                    ):

                        payment.mark_cancelled(
                            "SSLCommerz cancelled the payment."
                        )

                    elif (
                        gateway_status
                        == "EXPIRED"
                    ):

                        payment.mark_failed(
                            "SSLCommerz payment expired."
                        )

                    elif (
                        gateway_status
                        == "UNATTEMPTED"
                    ):

                        payment.mark_failed(
                            "No payment channel was completed."
                        )

                    else:

                        payment.mark_failed(
                            "SSLCommerz reported payment failure."
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
                        ],
                    )

        # ==================================================
        # UNKNOWN STATUS
        # ==================================================

        else:

            with transaction.atomic():

                payment = (
                    Payment.objects
                    .select_for_update()
                    .get(
                        pk=payment.pk,
                    )
                )

                payment.gateway_response = dict(
                    request.data
                )

                payment.save(
                    update_fields=[
                        "gateway_response",
                        "updated_at",
                    ],
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
        # Lock order
        # --------------------------------------------------

        order = get_object_or_404(
            Order.objects.select_for_update(),
            id=order_id,
            customer=request.user,
        )

        # --------------------------------------------------
        # SSLCommerz only
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
        # Invalid states
        # --------------------------------------------------

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
        # CREATE SESSION
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
                ],
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
            ],
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

    def get(
        self,
        request,
        order_id,
    ):

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
    def post(
        self,
        request,
        order_id,
    ):

        # --------------------------------------------------
        # Lock order
        # --------------------------------------------------

        order = get_object_or_404(
            Order.objects.select_for_update(),
            id=order_id,
            customer=request.user,
        )

        # --------------------------------------------------
        # SSLCommerz only
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
        # Pending only
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
        # CREATE SESSION
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
                ],
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
            ],
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