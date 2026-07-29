from django.urls import path

from .views import (
    ProductListCreateView,
    ProductRetrieveUpdateDeleteView,
)

urlpatterns = [

    path(
        "",
        ProductListCreateView.as_view()
    ),

    path(
        "<int:pk>/",
        ProductRetrieveUpdateDeleteView.as_view()
    ),

]