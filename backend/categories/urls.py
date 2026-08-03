from django.urls import path

from .views import (
    CategoryListCreateView,
    CategoryRetrieveUpdateDeleteView,
)

urlpatterns = [

    path(
        "",
        CategoryListCreateView.as_view()
    ),

    path(
        "<int:pk>/",
        CategoryRetrieveUpdateDeleteView.as_view()
    ),

]