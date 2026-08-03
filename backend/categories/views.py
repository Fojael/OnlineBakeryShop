from rest_framework import generics
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from accounts.permissions import IsAdmin

from .models import Category
from .serializers import CategorySerializer


class CategoryListCreateView(
    generics.ListCreateAPIView
):

    queryset = Category.objects.all()

    serializer_class = CategorySerializer

    def get_permissions(self):

        if self.request.method == "POST":
            return [IsAdmin()]

        return [IsAuthenticatedOrReadOnly()]

    def get_serializer_context(self):

        return {
            "request": self.request
        }


class CategoryRetrieveUpdateDeleteView(
    generics.RetrieveUpdateDestroyAPIView
):

    queryset = Category.objects.all()

    serializer_class = CategorySerializer

    def get_permissions(self):

        if self.request.method in [
            "PUT",
            "DELETE",
        ]:
            return [IsAdmin()]

        return [IsAuthenticatedOrReadOnly()]

    def get_serializer_context(self):

        return {
            "request": self.request
        }