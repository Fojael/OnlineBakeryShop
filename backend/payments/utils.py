import uuid


def generate_transaction_id():
    """
    Generate a unique SSLCommerz transaction ID.
    """

    return uuid.uuid4().hex.upper()


def get_customer_name(user):

    try:
        full_name = user.get_full_name()

    except AttributeError:
        full_name = ""

    if full_name:
        return full_name.strip()

    return getattr(
        user,
        "username",
        "",
    ) or "Customer"


def get_customer_email(user):

    return (
        getattr(
            user,
            "email",
            "",
        )
        or "customer@example.com"
    )


def get_customer_phone(user):

    return (
        getattr(
            user,
            "phone",
            "",
        )
        or "01700000000"
    )


def get_shipping_address(order):

    address = getattr(
        order,
        "shipping_address",
        "",
    )

    if address is None:
        return ""

    return str(address).strip()


def clean_sslcommerz_text(
    value,
    max_length=200,
):

    if value is None:
        return ""

    return str(value).strip()[:max_length]