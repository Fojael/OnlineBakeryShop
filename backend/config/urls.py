from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path

from .views import home

urlpatterns = [
    path("", home),

    path("admin/", admin.site.urls),

    path("api/auth/", include("accounts.urls")),
    path("api/products/", include("products.urls")),
    path(
    "api/categories/",
    include("categories.urls")
     ),
    path(
        "api/inventory/",
        include("inventory.urls"),
    ),
    path("api/payments/", include("payments.urls")),
    path("api/suppliers/", include("suppliers.urls")),
    path("api/orders/", include("orders.urls")),
    path(
        "api/cart/",
        include("cart.urls")
    ),
    path(
        "api/wishlist/",
        include("wishlist.urls"),
    ),
    path(
        "api/address/",
        include("address.urls"),
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )