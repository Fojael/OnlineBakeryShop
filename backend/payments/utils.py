from urllib.parse import urlencode

from django.conf import settings


def frontend_redirect(
    path,
    order_id=None,
    payment_id=None,
    tran_id=None,
    reason=None,
):
    """
    Build frontend redirect URL.

    Example:

    http://localhost:5173/checkout/success?order_id=10
    """

    base_url = getattr(
        settings,
        "FRONTEND_URL",
        "http://localhost:5173",
    ).rstrip("/")


    params = {}


    if order_id is not None:

        params["order_id"] = order_id


    if payment_id is not None:

        params["payment_id"] = payment_id


    if tran_id:

        params["tran_id"] = tran_id


    if reason:

        params["reason"] = reason


    url = (
        f"{base_url}{path}"
    )


    if params:

        url += (
            "?"
            +
            urlencode(
                params
            )
        )


    return url