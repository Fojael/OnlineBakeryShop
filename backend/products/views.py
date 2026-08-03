from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from accounts.permissions import IsAdmin

from .models import Product
from .serializers import ProductSerializer


class ProductListCreateView(generics.ListCreateAPIView):

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):

        if self.request.method == "POST":
            return [IsAdmin()]

        return [IsAuthenticatedOrReadOnly()]

    def get_serializer_context(self):
        return {
            "request": self.request
        }


class ProductRetrieveUpdateDeleteView(
    generics.RetrieveUpdateDestroyAPIView
):

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):

        if self.request.method in ["PUT", "PATCH", "DELETE"]:
            return [IsAdmin()]

        return [IsAuthenticatedOrReadOnly()]

    def get_serializer_context(self):
        return {
            "request": self.request
        }