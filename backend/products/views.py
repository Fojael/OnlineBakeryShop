from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Product
from .serializers import ProductSerializer
from accounts.permissions import IsAdmin


class ProductListCreateView(
    generics.ListCreateAPIView
):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):

        if self.request.method == "POST":
            return [IsAdmin()]

        return [IsAuthenticatedOrReadOnly()]


class ProductRetrieveUpdateDeleteView(
    generics.RetrieveUpdateDestroyAPIView
):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):

        if self.request.method in ["PUT", "DELETE"]:
            return [IsAdmin()]

        return [IsAuthenticatedOrReadOnly()]