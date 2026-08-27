# payments/services.py

import uuid

import requests

from django.conf import settings


class SSLCommerzGateway:
    """
    SSLCommerz Payment Gateway Service.

    Handles:
        1. Payment session creation
        2. SSLCommerz transaction validation
    """

    def __init__(self):
        # ======================================================
        # SSLCommerz Configuration
        # ======================================================

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
            "https://sandbox.sslcommerz.com/gwprocess/v4/api.php",
        )

        # ------------------------------------------------------
        # Validation API
        # ------------------------------------------------------

        self.validation_url = getattr(
            settings,
            "SSLCOMMERZ_VALIDATION_URL",
            "https://sandbox.sslcommerz.com/"
            "validator/api/validationserverAPI.php",
        )

        # ------------------------------------------------------
        # Request timeout
        # ------------------------------------------------------

        self.timeout = getattr(
            settings,
            "SSLCOMMERZ_TIMEOUT",
            30,
        )

    # ==========================================================
    # Generate Transaction ID
    # ==========================================================

    def generate_transaction_id(self):
        """
        Generate a unique transaction ID.

        SSLCommerz requires tran_id to uniquely identify
        a payment transaction.
        """

        return uuid.uuid4().hex.upper()

    # ==========================================================
    # Create Payment Session
    # ==========================================================

    def create_session(
        self,
        order,
        customer,
    ):
        """
        Create an SSLCommerz payment session.

        Returns:
            (
                transaction_id,
                sslcommerz_response
            )
        """

        transaction_id = self.generate_transaction_id()

        # ======================================================
        # Customer Information
        # ======================================================

        customer_name = (
            customer.get_full_name()
            or customer.username
        )

        customer_email = (
            customer.email
            or "customer@example.com"
        )

        customer_phone = getattr(
            customer,
            "phone",
            "",
        )

        if not customer_phone:
            customer_phone = "01700000000"

        # ======================================================
        # Shipping Address
        # ======================================================

        shipping_address = getattr(
            order,
            "shipping_address",
            "",
        )

        if not shipping_address:
            shipping_address = "Dhaka, Bangladesh"

        # ======================================================
        # Payment Amount
        # ======================================================

        total_amount = str(
            order.total_amount
        )

        # ======================================================
        # Callback URLs
        # ======================================================

        success_url = getattr(
            settings,
            "SSLCOMMERZ_SUCCESS_URL",
            "",
        )

        fail_url = getattr(
            settings,
            "SSLCOMMERZ_FAIL_URL",
            "",
        )

        cancel_url = getattr(
            settings,
            "SSLCOMMERZ_CANCEL_URL",
            "",
        )

        ipn_url = getattr(
            settings,
            "SSLCOMMERZ_IPN_URL",
            "",
        )

        # ======================================================
        # SSLCommerz Payload
        # ======================================================

        payload = {
            # --------------------------------------------------
            # Store Credentials
            # --------------------------------------------------

            "store_id": self.store_id,

            "store_passwd": self.store_password,

            # --------------------------------------------------
            # Transaction
            # --------------------------------------------------

            "total_amount": total_amount,

            "currency": "BDT",

            "tran_id": transaction_id,

            # --------------------------------------------------
            # Callback URLs
            # --------------------------------------------------

            "success_url": success_url,

            "fail_url": fail_url,

            "cancel_url": cancel_url,

            "ipn_url": ipn_url,

            # --------------------------------------------------
            # Product Information
            # --------------------------------------------------

            "shipping_method": "Courier",

            "product_name": (
                f"Bakery Order #{order.id}"
            ),

            "product_category": "Bakery",

            "product_profile": "general",

            # --------------------------------------------------
            # Customer Information
            # --------------------------------------------------

            "cus_name": customer_name,

            "cus_email": customer_email,

            "cus_add1": shipping_address,

            "cus_city": "Dhaka",

            "cus_state": "Dhaka",

            "cus_postcode": "1200",

            "cus_country": "Bangladesh",

            "cus_phone": customer_phone,

            "cus_fax": "",

            # --------------------------------------------------
            # Shipping Information
            # --------------------------------------------------

            "ship_name": customer_name,

            "ship_add1": shipping_address,

            "ship_city": "Dhaka",

            "ship_state": "Dhaka",

            "ship_postcode": "1200",

            "ship_country": "Bangladesh",
        }

        # ======================================================
        # Send Payment Request
        # ======================================================

        response = requests.post(
            self.base_url,
            data=payload,
            timeout=self.timeout,
        )

        # ------------------------------------------------------
        # Raise HTTP errors
        # ------------------------------------------------------

        response.raise_for_status()

        # ======================================================
        # Parse SSLCommerz Response
        # ======================================================

        try:

            response_data = response.json()

        except ValueError as exc:

            raise requests.RequestException(
                "SSLCommerz returned an invalid JSON response."
            ) from exc

        return (
            transaction_id,
            response_data,
        )

    # ==========================================================
    # Validate Payment
    # ==========================================================

    def validate_payment(
        self,
        validation_id,
    ):
        """
        Validate a completed SSLCommerz transaction.

        Parameters:
            validation_id:
                SSLCommerz val_id.

        Returns:
            SSLCommerz validation response.
        """

        # ======================================================
        # Validate Input
        # ======================================================

        if not validation_id:

            raise ValueError(
                "SSLCommerz validation ID is required."
            )

        # ======================================================
        # Validation Parameters
        # ======================================================

        params = {
            "val_id": validation_id,

            "store_id": self.store_id,

            "store_passwd": self.store_password,

            "format": "json",
        }

        # ======================================================
        # Send Validation Request
        # ======================================================

        response = requests.get(
            self.validation_url,
            params=params,
            timeout=self.timeout,
        )

        # ------------------------------------------------------
        # Raise HTTP errors
        # ------------------------------------------------------

        response.raise_for_status()

        # ======================================================
        # Parse Response
        # ======================================================

        try:

            response_data = response.json()

        except ValueError as exc:

            raise requests.RequestException(
                "SSLCommerz validation returned invalid JSON."
            ) from exc

        return response_data