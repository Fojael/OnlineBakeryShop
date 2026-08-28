import requests

from django.conf import settings

from .utils import (
    generate_transaction_id,
    get_customer_name,
    get_customer_email,
    get_customer_phone,
    get_shipping_address,
    clean_sslcommerz_text,
)


class SSLCommerzGateway:

    """
    SSLCommerz payment gateway service.

    Handles:

    1. Payment session creation
    2. Payment validation
    """

    # ==========================================================
    # INITIALIZATION
    # ==========================================================

    def __init__(self):

        self.store_id = getattr(
            settings,
            "SSLCOMMERZ_STORE_ID",
            "",
        )

        self.store_password = getattr(
            settings,
            "SSLCOMMERZ_STORE_PASSWORD",
            "",
        )

        self.base_url = getattr(
            settings,
            "SSLCOMMERZ_API_URL",
            "",
        )

        self.validation_url = getattr(
            settings,
            "SSLCOMMERZ_VALIDATION_URL",
            "",
        )

        self.timeout = getattr(
            settings,
            "SSLCOMMERZ_TIMEOUT",
            30,
        )

        if not self.store_id:
            raise ValueError(
                "SSLCOMMERZ_STORE_ID is not configured."
            )

        if not self.store_password:
            raise ValueError(
                "SSLCOMMERZ_STORE_PASSWORD is not configured."
            )

        if not self.base_url:
            raise ValueError(
                "SSLCOMMERZ_API_URL is not configured."
            )

        if not self.validation_url:

            if (
                "securepay.sslcommerz.com"
                in self.base_url
            ):

                self.validation_url = (
                    "https://securepay.sslcommerz.com"
                    "/validator/api/validationserverAPI.php"
                )

            else:

                self.validation_url = (
                    "https://sandbox.sslcommerz.com"
                    "/validator/api/validationserverAPI.php"
                )

    # ==========================================================
    # TRANSACTION ID
    # ==========================================================

    def generate_transaction_id(self):

        return generate_transaction_id()

    # ==========================================================
    # CREATE SESSION
    # ==========================================================

    def create_session(
        self,
        order,
        customer,
    ):

        transaction_id = (
            self.generate_transaction_id()
        )

        customer_name = clean_sslcommerz_text(
            get_customer_name(customer),
            100,
        )

        customer_email = clean_sslcommerz_text(
            get_customer_email(customer),
            100,
        )

        customer_phone = clean_sslcommerz_text(
            get_customer_phone(customer),
            20,
        )

        shipping_address = clean_sslcommerz_text(
            get_shipping_address(order),
            200,
        )

        if not shipping_address:
            shipping_address = (
                "Dhaka, Bangladesh"
            )

        total_amount = str(
            order.total_amount
        )

        payload = {

            # --------------------------------------------------
            # Credentials
            # --------------------------------------------------

            "store_id": self.store_id,
            "store_passwd": self.store_password,

            # --------------------------------------------------
            # Payment
            # --------------------------------------------------

            "total_amount": total_amount,
            "currency": "BDT",
            "tran_id": transaction_id,

            # --------------------------------------------------
            # Callbacks
            # --------------------------------------------------

            "success_url": (
                settings.SSLCOMMERZ_SUCCESS_URL
            ),

            "fail_url": (
                settings.SSLCOMMERZ_FAIL_URL
            ),

            "cancel_url": (
                settings.SSLCOMMERZ_CANCEL_URL
            ),

            "ipn_url": (
                settings.SSLCOMMERZ_IPN_URL
            ),

            # --------------------------------------------------
            # Product
            # --------------------------------------------------

            "shipping_method": "Courier",

            "product_name": (
                f"Bakery Order #{order.id}"
            ),

            "product_category": "Bakery",

            "product_profile": "general",

            # --------------------------------------------------
            # Customer
            # --------------------------------------------------

            "cus_name": customer_name,
            "cus_email": customer_email,

            "cus_add1": shipping_address,
            "cus_add2": "",

            "cus_city": "Dhaka",
            "cus_state": "Dhaka",
            "cus_postcode": "1200",

            "cus_country": "Bangladesh",
            "cus_phone": customer_phone,
            "cus_fax": "",

            # --------------------------------------------------
            # Shipping
            # --------------------------------------------------

            "ship_name": customer_name,

            "ship_add1": shipping_address,
            "ship_add2": "",

            "ship_city": "Dhaka",
            "ship_state": "Dhaka",
            "ship_postcode": "1200",

            "ship_country": "Bangladesh",
        }

        try:

            response = requests.post(
                self.base_url,
                data=payload,
                timeout=self.timeout,
            )

            response.raise_for_status()

        except requests.RequestException as exc:

            raise requests.RequestException(
                "SSLCommerz payment session "
                "request failed."
            ) from exc

        try:

            response_data = response.json()

        except ValueError as exc:

            raise requests.RequestException(
                "SSLCommerz returned invalid JSON."
            ) from exc

        return (
            transaction_id,
            response_data,
        )

    # ==========================================================
    # VALIDATE PAYMENT
    # ==========================================================

    def validate_payment(
        self,
        validation_id,
    ):

        if not validation_id:

            raise ValueError(
                "SSLCommerz validation ID "
                "is required."
            )

        params = {

            "val_id": validation_id,

            "store_id": self.store_id,

            "store_passwd": self.store_password,

            "format": "json",
        }

        try:

            response = requests.get(
                self.validation_url,
                params=params,
                timeout=self.timeout,
            )

            response.raise_for_status()

        except requests.RequestException as exc:

            raise requests.RequestException(
                "SSLCommerz validation request failed."
            ) from exc

        try:

            response_data = response.json()

        except ValueError as exc:

            raise requests.RequestException(
                "SSLCommerz validation returned "
                "invalid JSON."
            ) from exc

        return response_data