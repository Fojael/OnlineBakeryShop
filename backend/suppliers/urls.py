from django.urls import path

from .views import (
    SupplierListCreateView,
    SupplierRetrieveUpdateDestroyView,
)

urlpatterns = [
    path("", SupplierListCreateView.as_view()),
    path("<int:pk>/", SupplierRetrieveUpdateDestroyView.as_view()),
]