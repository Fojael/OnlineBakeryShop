import json
from decimal import Decimal

import requests
from django.conf import settings


class SSLCommerzError(Exception):
    """Custom exception for SSLCommerz-related errors."""
    pass


# ==========================================================
# BASE URL
# ==========================================================

def _base_url():
    if settings.SSLCOMMERZ_IS_SANDBOX:
        return "https://sandbox.sslcommerz.com"

    return "https://securepay.sslcommerz.com"


# ==========================================================
# GATEWAY URL
# ==========================================================

def _gateway_api_url():
    if settings.SSLCOMMERZ_IS_SANDBOX:
        return (
            "https://sandbox.sslcommerz.com"
            "/gwprocess/v4/api.php"
        )

    return (
        "https://securepay.sslcommerz.com"
        "/gwprocess/v4/api.php"
    )


# ==========================================================
# VALIDATE SETTINGS
# ==========================================================

def _validate_configuration():

    store_id = str(
        settings.SSLCOMMERZ_STORE_ID or ""
    ).strip()

    store_password = str(
        settings.SSLCOMMERZ_STORE_PASSWORD or ""
    ).strip()

    public_backend_url = str(
        settings.PUBLIC_BACKEND_URL or ""
    ).strip().rstrip("/")

    # ------------------------------------------------------
    # STORE ID
    # ------------------------------------------------------

    if not store_id:

        raise SSLCommerzError(
            "SSLCommerz Store ID is not configured."
        )

    if store_id.lower() in {
        "your_real_sandbox_store_id",
        "your_sandbox_store_id",
        "your_store_id",
    }:

        raise SSLCommerzError(
            "Replace the placeholder SSLCommerz Store ID "
            "with your real sandbox Store ID."
        )

    # ------------------------------------------------------
    # STORE PASSWORD
    # ------------------------------------------------------

    if not store_password:

        raise SSLCommerzError(
            "SSLCommerz Store Password is not configured."
        )

    if store_password.lower() in {
        "your_real_sandbox_store_password",
        "your_sandbox_store_password",
        "your_store_password",
    }:

        raise SSLCommerzError(
            "Replace the placeholder SSLCommerz Store Password "
            "with your real sandbox password."
        )

    # ------------------------------------------------------
    # PUBLIC BACKEND URL
    # ------------------------------------------------------

    if not public_backend_url:

        raise SSLCommerzError(
            "PUBLIC_BACKEND_URL is not configured."
        )

    if "YOUR_PUBLIC_HTTPS_BACKEND_URL" in public_backend_url:

        raise SSLCommerzError(
            "Replace YOUR_PUBLIC_HTTPS_BACKEND_URL "
            "with your actual public HTTPS backend URL."
        )

    if "localhost" in public_backend_url.lower():

        raise SSLCommerzError(
            "PUBLIC_BACKEND_URL cannot use localhost. "
            "SSLCommerz needs a publicly accessible backend URL."
        )

    if "127.0.0.1" in public_backend_url:

        raise SSLCommerzError(
            "PUBLIC_BACKEND_URL cannot use 127.0.0.1. "
            "SSLCommerz needs a publicly accessible backend URL."
        )

    if not public_backend_url.startswith("https://"):

        raise SSLCommerzError(
            "PUBLIC_BACKEND_URL must use HTTPS."
        )


# ==========================================================
# SAFE STRING
# ==========================================================

def _safe_string(value, max_length=255):

    if value is None:
        return ""

    return str(value).strip()[:max_length]


# ==========================================================
# INITIATE PAYMENT
# ==========================================================

def initiate_payment(payment):

    _validate_configuration()

    order = payment.order
    customer = order.customer

    amount = Decimal(payment.amount)

    # ======================================================
    # AMOUNT
    # ======================================================

    if amount < Decimal("10.00"):

        raise SSLCommerzError(
            "SSLCommerz requires a transaction amount "
            "of at least 10.00 BDT."
        )

    if amount > Decimal("500000.00"):

        raise SSLCommerzError(
            "SSLCommerz transaction amount cannot exceed "
            "500000.00 BDT."
        )

    # ======================================================
    # ORDER ITEMS
    # ======================================================

    order_items = (
        order.items
        .select_related("product")
        .all()
    )

    if not order_items.exists():

        raise SSLCommerzError(
            "Cannot create payment for an empty order."
        )

    product_names = []
    cart_items = []

    for item in order_items:

        if not item.product:

            raise SSLCommerzError(
                "An order item has no associated product."
            )

        product_name = _safe_string(
            item.product.name,
            255,
        )

        product_names.append(product_name)

        cart_items.append(
            {
                "sku": str(item.product_id),
                "product": product_name,
                "quantity": str(item.quantity),
                "amount": str(item.subtotal),
                "unit_price": str(item.price),
            }
        )

    # ======================================================
    # CUSTOMER NAME
    # ======================================================

    customer_name = ""

    if hasattr(customer, "get_full_name"):

        customer_name = (
            customer.get_full_name()
            or ""
        )

    if not customer_name:

        customer_name = getattr(
            customer,
            "username",
            "",
        )

    if not customer_name:

        customer_name = "Customer"

    customer_name = _safe_string(
        customer_name,
        50,
    )

    # ======================================================
    # EMAIL
    # ======================================================

    customer_email = _safe_string(
        getattr(
            customer,
            "email",
            "",
        ),
        50,
    )

    if not customer_email:

        raise SSLCommerzError(
            "Customer email is required."
        )

    # ======================================================
    # PHONE
    # ======================================================

    customer_phone = _safe_string(
        getattr(
            customer,
            "phone",
            "",
        ),
        20,
    )

    if not customer_phone:

        customer_phone = "01700000000"

    # ======================================================
    # SHIPPING ADDRESS
    # ======================================================

    shipping_address = _safe_string(
        getattr(
            order,
            "shipping_address",
            "",
        ),
        50,
    )

    if not shipping_address:

        shipping_address = "Dhaka"

    # ======================================================
    # CALLBACK URLS
    # ======================================================

    callback_urls = {

        "success_url":
            settings.SSLCOMMERZ_SUCCESS_URL,

        "fail_url":
            settings.SSLCOMMERZ_FAIL_URL,

        "cancel_url":
            settings.SSLCOMMERZ_CANCEL_URL,

        "ipn_url":
            settings.SSLCOMMERZ_IPN_URL,
    }

    for name, value in callback_urls.items():

        value = str(value or "").strip()

        if not value:

            raise SSLCommerzError(
                f"{name} is not configured."
            )

        if "YOUR_PUBLIC_HTTPS_BACKEND_URL" in value:

            raise SSLCommerzError(
                f"{name} still contains "
                "YOUR_PUBLIC_HTTPS_BACKEND_URL."
            )

        if "localhost" in value.lower():

            raise SSLCommerzError(
                f"{name} cannot use localhost. "
                "SSLCommerz requires a public backend URL."
            )

        if "127.0.0.1" in value:

            raise SSLCommerzError(
                f"{name} cannot use 127.0.0.1. "
                "SSLCommerz requires a public backend URL."
            )

        if not value.startswith("https://"):

            raise SSLCommerzError(
                f"{name} must use HTTPS."
            )

    # ======================================================
    # REQUEST DATA
    # ======================================================

    data = {

        # --------------------------------------------------
        # STORE
        # --------------------------------------------------

        "store_id":
            settings.SSLCOMMERZ_STORE_ID,

        "store_passwd":
            settings.SSLCOMMERZ_STORE_PASSWORD,

        # --------------------------------------------------
        # PAYMENT
        # --------------------------------------------------

        "total_amount":
            f"{amount:.2f}",

        "currency":
            payment.currency,

        "tran_id":
            payment.transaction_id,

        # --------------------------------------------------
        # CALLBACKS
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
            customer_email,

        "cus_add1":
            shipping_address,

        "cus_city":
            "Dhaka",

        "cus_state":
            "Dhaka",

        "cus_postcode":
            "1000",

        "cus_country":
            "Bangladesh",

        "cus_phone":
            customer_phone,

        # --------------------------------------------------
        # SHIPPING
        # --------------------------------------------------

        "shipping_method":
            "YES",

        "ship_name":
            customer_name,

        "ship_add1":
            shipping_address,

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

        "num_of_item":
            str(order_items.count()),

        "product_name":
            ", ".join(product_names)[:255],

        "product_category":
            "Bakery",

        "product_profile":
            "physical-goods",

        "product_amount":
            f"{Decimal(order.subtotal):.2f}",

        "vat":
            "0.00",

        "discount_amount":
            "0.00",

        "convenience_fee":
            f"{Decimal(order.delivery_charge):.2f}",

        "cart":
            json.dumps(cart_items),

        # --------------------------------------------------
        # CUSTOM
        # --------------------------------------------------

        "value_a":
            str(order.id),
    }

    # ======================================================
    # REQUEST
    # ======================================================

    url = _gateway_api_url()

    try:

        response = requests.post(
            url,
            data=data,
            timeout=(10, 40),
        )

    except requests.Timeout as exc:

        raise SSLCommerzError(
            "SSLCommerz request timed out."
        ) from exc

    except requests.RequestException as exc:

        raise SSLCommerzError(
            f"Could not connect to SSLCommerz: {exc}"
        ) from exc

    # ======================================================
    # HTTP ERROR
    # ======================================================

    if response.status_code != 200:

        body = response.text[:1000]

        raise SSLCommerzError(
            "SSLCommerz returned HTTP "
            f"{response.status_code}: {body}"
        )

    # ======================================================
    # JSON
    # ======================================================

    try:

        payload = response.json()

    except ValueError as exc:

        raise SSLCommerzError(
            "SSLCommerz returned an invalid JSON response."
        ) from exc

    # ======================================================
    # GATEWAY STATUS
    # ======================================================

    gateway_status = str(
        payload.get(
            "status",
            "",
        )
    ).upper()

    if gateway_status != "SUCCESS":

        reason = (
            payload.get("failedreason")
            or payload.get("failedReason")
            or payload.get("message")
            or payload.get("error")
            or "SSLCommerz could not create the payment session."
        )

        raise SSLCommerzError(
            str(reason)
        )

    # ======================================================
    # GATEWAY URL
    # ======================================================

    gateway_url = (
        payload.get("GatewayPageURL")
        or payload.get("redirectGatewayURL")
    )

    if not gateway_url:

        raise SSLCommerzError(
            "SSLCommerz did not return a gateway URL."
        )

    return payload, gateway_url


# ==========================================================
# VALIDATE TRANSACTION
# ==========================================================

def validate_transaction(val_id):

    _validate_configuration()

    val_id = str(
        val_id or ""
    ).strip()

    if not val_id:

        raise SSLCommerzError(
            "Validation ID is required."
        )

    params = {

        "val_id":
            val_id,

        "store_id":
            settings.SSLCOMMERZ_STORE_ID,

        "store_passwd":
            settings.SSLCOMMERZ_STORE_PASSWORD,

        "format":
            "json",
    }

    url = (
        f"{_base_url()}"
        "/validator/api/"
        "validationserverAPI.php"
    )

    try:

        response = requests.get(
            url,
            params=params,
            timeout=(10, 40),
        )

    except requests.Timeout as exc:

        raise SSLCommerzError(
            "SSLCommerz validation request timed out."
        ) from exc

    except requests.RequestException as exc:

        raise SSLCommerzError(
            f"Could not validate SSLCommerz payment: {exc}"
        ) from exc

    # ======================================================
    # HTTP ERROR
    # ======================================================

    if response.status_code != 200:

        body = response.text[:1000]

        raise SSLCommerzError(
            "SSLCommerz validation API returned "
            f"HTTP {response.status_code}: {body}"
        )

    # ======================================================
    # JSON
    # ======================================================

    try:

        payload = response.json()

    except ValueError as exc:

        raise SSLCommerzError(
            "SSLCommerz validation API returned "
            "invalid JSON."
        ) from exc

    return payload