import json
from decimal import Decimal

import requests
from django.conf import settings


class SSLCommerzError(Exception):
    pass


# ==========================================================
# BASE URL
# ==========================================================

def _base_url():

    if settings.SSLCOMMERZ_IS_SANDBOX:

        return (
            "https://sandbox.sslcommerz.com"
        )

    return (
        "https://securepay.sslcommerz.com"
    )


# ==========================================================
# INITIATE PAYMENT
# ==========================================================

def initiate_payment(payment):

    order = payment.order

    customer = order.customer

    amount = Decimal(
        payment.amount
    )

    # ======================================================
    # AMOUNT VALIDATION
    # ======================================================

    if amount < Decimal("10.00"):

        raise SSLCommerzError(
            "SSLCommerz requires a transaction "
            "amount of at least 10.00 BDT."
        )

    if amount > Decimal("500000.00"):

        raise SSLCommerzError(
            "SSLCommerz transaction amount "
            "cannot exceed 500000.00 BDT."
        )

    # ======================================================
    # CONFIGURATION
    # ======================================================

    if not settings.SSLCOMMERZ_STORE_ID:

        raise SSLCommerzError(
            "SSLCommerz store ID is not configured."
        )

    if not settings.SSLCOMMERZ_STORE_PASSWORD:

        raise SSLCommerzError(
            "SSLCommerz store password is not configured."
        )

    # ======================================================
    # ORDER ITEMS
    # ======================================================

    product_names = []

    cart = []

    for item in (
        order.items
        .select_related("product")
        .all()
    ):

        product_names.append(
            item.product.name
        )

        cart.append(
            {
                "sku": str(
                    item.product_id
                ),
                "product": (
                    item.product.name[:255]
                ),
                "quantity": str(
                    item.quantity
                ),
                "amount": str(
                    item.subtotal
                ),
                "unit_price": str(
                    item.price
                ),
            }
        )

    # ======================================================
    # CUSTOMER NAME
    # ======================================================

    customer_name = (
        getattr(
            customer,
            "get_full_name",
            lambda: "",
        )()
        or getattr(
            customer,
            "username",
            "",
        )
        or "Customer"
    )

    customer_name = customer_name[:50]

    # ======================================================
    # PHONE
    # ======================================================

    customer_phone = getattr(
        customer,
        "phone",
        "",
    )

    # ======================================================
    # REQUEST DATA
    # ======================================================

    data = {

        "store_id":
            settings.SSLCOMMERZ_STORE_ID,

        "store_passwd":
            settings.SSLCOMMERZ_STORE_PASSWORD,

        "total_amount":
            f"{amount:.2f}",

        "currency":
            payment.currency,

        "tran_id":
            payment.transaction_id,

        # --------------------------------------------------
        # CALLBACK URLS
        # --------------------------------------------------

        "success_url":
            settings.SSLCOMMERZ_SUCCESS_URL,

        "fail_url":
            settings.SSLCOMMERZ_FAIL_URL,

        "cancel_url":
            settings.SSLCOMMERZ_CANCEL_URL,

        "ipn_url":
            settings.SSLCOMMERZ_IPN_URL,

        # --------------------------------------------------
        # CUSTOMER
        # --------------------------------------------------

        "cus_name":
            customer_name,

        "cus_email":
            customer.email[:50],

        "cus_add1":
            order.shipping_address[:50],

        "cus_city":
            "Dhaka",

        "cus_state":
            "Dhaka",

        "cus_postcode":
            "1000",

        "cus_country":
            "Bangladesh",

        "cus_phone":
            str(customer_phone)[:20],

        # --------------------------------------------------
        # SHIPPING
        # --------------------------------------------------

        "ship_name":
            customer_name,

        "ship_add1":
            order.shipping_address[:50],

        "ship_city":
            "Dhaka",

        "ship_state":
            "Dhaka",

        "ship_postcode":
            "1000",

        "ship_country":
            "Bangladesh",

        # --------------------------------------------------
        # PRODUCT
        # --------------------------------------------------

        "shipping_method":
            "YES",

        "num_of_item":
            str(order.items.count()),

        "product_name":
            ", ".join(
                product_names
            )[:255],

        "product_category":
            "Bakery",

        "product_profile":
            "physical-goods",

        "product_amount":
            f"{order.subtotal:.2f}",

        "vat":
            "0.00",

        "discount_amount":
            "0.00",

        "convenience_fee":
            f"{order.delivery_charge:.2f}",

        "cart":
            json.dumps(cart),

        # --------------------------------------------------
        # CUSTOM VALUE
        # --------------------------------------------------

        "value_a":
            str(order.id),
    }

    # ======================================================
    # API URL
    # ======================================================

    url = (
        f"{_base_url()}"
        "/gwprocess/v4/api.php"
    )

    # ======================================================
    # REQUEST
    # ======================================================

    try:

        response = requests.post(
            url,
            data=data,
            timeout=30,
        )

        response.raise_for_status()

        payload = response.json()

    except (
        requests.RequestException,
        ValueError,
    ) as exc:

        raise SSLCommerzError(
            f"Could not connect to SSLCommerz: {exc}"
        ) from exc

    # ======================================================
    # GATEWAY STATUS
    # ======================================================

    if payload.get("status") != "SUCCESS":

        raise SSLCommerzError(
            payload.get("failedreason")
            or
            "SSLCommerz could not create "
            "the payment session."
        )

    # ======================================================
    # GATEWAY URL
    # ======================================================

    gateway_url = (
        payload.get("GatewayPageURL")
        or
        payload.get(
            "redirectGatewayURL"
        )
    )

    if not gateway_url:

        raise SSLCommerzError(
            "SSLCommerz did not return "
            "a gateway URL."
        )

    return payload, gateway_url


# ==========================================================
# VALIDATE TRANSACTION
# ==========================================================

def validate_transaction(
    val_id,
):

    if not val_id:

        raise SSLCommerzError(
            "Validation ID is required."
        )

    # ======================================================
    # CONFIG
    # ======================================================

    if not settings.SSLCOMMERZ_STORE_ID:

        raise SSLCommerzError(
            "SSLCommerz store ID is not configured."
        )

    if not settings.SSLCOMMERZ_STORE_PASSWORD:

        raise SSLCommerzError(
            "SSLCommerz store password is not configured."
        )

    # ======================================================
    # PARAMETERS
    # ======================================================

    params = {

        "val_id":
            str(val_id),

        "store_id":
            settings.SSLCOMMERZ_STORE_ID,

        "store_passwd":
            settings.SSLCOMMERZ_STORE_PASSWORD,

        "format":
            "json",
    }

    # ======================================================
    # URL
    # ======================================================

    url = (
        f"{_base_url()}"
        "/validator/api/"
        "validationserverAPI.php"
    )

    # ======================================================
    # REQUEST
    # ======================================================

    try:

        response = requests.get(
            url,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        payload = response.json()

    except (
        requests.RequestException,
        ValueError,
    ) as exc:

        raise SSLCommerzError(
            f"Could not validate SSLCommerz payment: {exc}"
        ) from exc

    return payload