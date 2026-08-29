from urllib.parse import urlencode

from django.conf import settings


def frontend_redirect(path, **params):

    base = settings.FRONTEND_URL.rstrip("/")

    query = urlencode(
        {
            key: value
            for key, value in params.items()
            if value is not None and value != ""
        }
    )

    return (
        f"{base}{path}"
        + (f"?{query}" if query else "")
    )