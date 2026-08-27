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

    # ==========================================================
    # INITIALIZATION
    # ==========================================================

    def __init__(self):
        self.store_id = settings.SSLCOMMERZ_STORE_ID
        self.store_password = settings.SSLCOMMERZ_STORE_PASSWORD
        self.base_url = settings.SSLCOMMERZ_API_URL

        # SSLCommerz validation endpoint
        self.validation_url = (
            "https://sandbox.sslcommerz.com"
            "/validator/api/validationserverAPI.php"
        )

    # ==========================================================
    # GENERATE TRANSACTION ID
    # ==========================================================

    def generate_transaction_id(self):
        """
        Generate a unique transaction ID.

        SSLCommerz requires a unique tran_id
        for every payment transaction.
        """

        return uuid.uuid4().hex.upper()

    # ==========================================================
    # CREATE PAYMENT SESSION
    # ==========================================================

    def create_session(self, order, customer):
        """
        Create an SSLCommerz payment session.

        Args:
            order:
                Django Order instance.

            customer:
                Authenticated customer/user.

        Returns:
            tuple:
                transaction_id,
                SSLCommerz response dictionary
        """

        transaction_id = self.generate_transaction_id()

        # ------------------------------------------------------
        # Customer Information
        # ------------------------------------------------------

        customer_name = (
            customer.get_full_name()
            or getattr(customer, "username", "")
            or "Customer"
        )

        customer_email = (
            getattr(customer, "email", "")
            or "customer@example.com"
        )

        customer_phone = getattr(
            customer,
            "phone",
            "",
        )

        # ------------------------------------------------------
        # Shipping Address
        # ------------------------------------------------------

        shipping_address = getattr(
            order,
            "shipping_address",
            "",
        )

        if not shipping_address:
            shipping_address = "Dhaka, Bangladesh"

        # ------------------------------------------------------
        # Payment Amount
        # ------------------------------------------------------

        total_amount = str(
            order.total_amount
        )

        # ------------------------------------------------------
        # SSLCommerz Payload
        # ------------------------------------------------------

        payload = {
            # Gateway credentials
            "store_id": self.store_id,
            "store_passwd": self.store_password,

            # Payment information
            "total_amount": total_amount,
            "currency": "BDT",
            "tran_id": transaction_id,

            # Callback URLs
            "success_url": settings.SSLCOMMERZ_SUCCESS_URL,
            "fail_url": settings.SSLCOMMERZ_FAIL_URL,
            "cancel_url": settings.SSLCOMMERZ_CANCEL_URL,
            "ipn_url": settings.SSLCOMMERZ_IPN_URL,

            # Product information
            "shipping_method": "Courier",
            "product_name": f"Bakery Order #{order.id}",
            "product_category": "Bakery",
            "product_profile": "general",

            # Customer information
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

            # Shipping information
            "ship_name": customer_name,
            "ship_add1": shipping_address,
            "ship_add2": "",
            "ship_city": "Dhaka",
            "ship_state": "Dhaka",
            "ship_postcode": "1200",
            "ship_country": "Bangladesh",
        }

        # ------------------------------------------------------
        # Send Request to SSLCommerz
        # ------------------------------------------------------

        response = requests.post(
            self.base_url,
            data=payload,
            timeout=30,
        )

        # Raise exception for HTTP errors
        response.raise_for_status()

        # ------------------------------------------------------
        # Parse JSON Response
        # ------------------------------------------------------

        try:
            response_data = response.json()

        except ValueError as exc:
            raise requests.RequestException(
                "SSLCommerz returned an invalid JSON response."
            ) from exc

        # ------------------------------------------------------
        # Return Transaction ID + Response
        # ------------------------------------------------------

        return (
            transaction_id,
            response_data,
        )

    # ==========================================================
    # VALIDATE PAYMENT
    # ==========================================================

    def validate_payment(self, validation_id):
        """
        Validate a completed SSLCommerz transaction.

        Args:
            validation_id:
                SSLCommerz val_id returned after payment.

        Returns:
            SSLCommerz validation response dictionary.
        """

        if not validation_id:
            raise ValueError(
                "SSLCommerz validation ID is required."
            )

        # ------------------------------------------------------
        # Validation Parameters
        # ------------------------------------------------------

        params = {
            "val_id": validation_id,
            "store_id": self.store_id,
            "store_passwd": self.store_password,
            "format": "json",
        }

        # ------------------------------------------------------
        # Send Validation Request
        # ------------------------------------------------------

        response = requests.get(
            self.validation_url,
            params=params,
            timeout=30,
        )

        response.raise_for_status()

        # ------------------------------------------------------
        # Parse JSON Response
        # ------------------------------------------------------

        try:
            response_data = response.json()

        except ValueError as exc:
            raise requests.RequestException(
                "SSLCommerz validation returned invalid JSON."
            ) from exc

        # ------------------------------------------------------
        # Return Validation Response
        # ------------------------------------------------------

        return response_data