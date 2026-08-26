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
        self.store_id = settings.SSLCOMMERZ_STORE_ID
        self.store_password = settings.SSLCOMMERZ_STORE_PASSWORD
        self.base_url = settings.SSLCOMMERZ_API_URL

        # SSLCommerz validation API
        self.validation_url = (
            "https://sandbox.sslcommerz.com"
            "/validator/api/validationserverAPI.php"
        )

    # ==========================================================
    # Generate Transaction ID
    # ==========================================================

    def generate_transaction_id(self):
        """
        Generate a unique transaction ID.

        SSLCommerz requires tran_id to uniquely identify
        the payment transaction.
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
            transaction_id
            SSLCommerz response
        """

        transaction_id = self.generate_transaction_id()

        # ------------------------------------------------------
        # Customer information
        # ------------------------------------------------------

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

        # ------------------------------------------------------
        # Shipping address
        # ------------------------------------------------------

        shipping_address = getattr(
            order,
            "shipping_address",
            "",
        )

        if not shipping_address:
            shipping_address = "Dhaka, Bangladesh"

        # ------------------------------------------------------
        # Payment payload
        # ------------------------------------------------------

        payload = {
            "store_id": self.store_id,
            "store_passwd": self.store_password,

            "total_amount": str(
                order.total_amount
            ),

            "currency": "BDT",

            "tran_id": transaction_id,

            # Callback URLs
            "success_url": settings.SSLCOMMERZ_SUCCESS_URL,
            "fail_url": settings.SSLCOMMERZ_FAIL_URL,
            "cancel_url": settings.SSLCOMMERZ_CANCEL_URL,
            "ipn_url": settings.SSLCOMMERZ_IPN_URL,

            # --------------------------------------------------
            # Product information
            # --------------------------------------------------

            "shipping_method": "Courier",

            "product_name": (
                f"Bakery Order #{order.id}"
            ),

            "product_category": "Bakery",

            "product_profile": "general",

            # --------------------------------------------------
            # Customer information
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
            # Shipping information
            # --------------------------------------------------

            "ship_name": customer_name,

            "ship_add1": shipping_address,

            "ship_city": "Dhaka",

            "ship_state": "Dhaka",

            "ship_postcode": "1200",

            "ship_country": "Bangladesh",
        }

        # ------------------------------------------------------
        # Send request to SSLCommerz
        # ------------------------------------------------------

        response = requests.post(
            self.base_url,
            data=payload,
            timeout=30,
        )

        # Raise exception for HTTP errors
        response.raise_for_status()

        # ------------------------------------------------------
        # Parse response
        # ------------------------------------------------------

        try:
            response_data = response.json()

        except ValueError:
            raise requests.RequestException(
                "SSLCommerz returned an invalid JSON response."
            )

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

        SSLCommerz returns a validation ID (val_id)
        after successful payment.

        The backend uses this ID to verify the transaction.
        """

        params = {
            "val_id": validation_id,

            "store_id": self.store_id,

            "store_passwd": self.store_password,

            "format": "json",
        }

        # ------------------------------------------------------
        # Send validation request
        # ------------------------------------------------------

        response = requests.get(
            self.validation_url,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        # ------------------------------------------------------
        # Parse response
        # ------------------------------------------------------

        try:
            response_data = response.json()

        except ValueError:
            raise requests.RequestException(
                "SSLCommerz validation returned invalid JSON."
            )

        return response_data