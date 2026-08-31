from urllib.parse import urlencode

from django.conf import settings


def frontend_redirect(path, **params):

    frontend_url = getattr(
        settings,
        "FRONTEND_URL",
        "http://localhost:5173",
    ).rstrip("/")

    path = "/" + path.lstrip("/")

    query_params = {
        key: value
        for key, value in params.items()
        if value is not None
        and value != ""
    }

    if query_params:

        return (
            f"{frontend_url}{path}"
            f"?{urlencode(query_params)}"
        )

    return f"{frontend_url}{path}"