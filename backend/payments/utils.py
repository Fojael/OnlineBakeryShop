import uuid


def generate_transaction_id():
    """
    Generate a unique transaction ID for SSLCommerz.
    """

    return uuid.uuid4().hex.upper()


def get_customer_name(user):
    """
    Return the customer's full name if available,
    otherwise fall back to the username.
    """

    full_name = user.get_full_name()

    if full_name:
        return full_name

    return user.username


def get_customer_phone(user):
    """
    Return customer's phone number if it exists.
    """

    return getattr(user, "phone", "")


def get_shipping_address(order):
    """
    Return shipping address as a string.
    """

    return order.shipping_address.strip()