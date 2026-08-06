from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Supplier
from .serializers import SupplierSerializer

from accounts.permissions import IsAdmin


class SupplierListCreateView(generics.ListCreateAPIView):
    queryset = Supplier.objects.all().order_by("-created_at")
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated, IsAdmin]


class SupplierRetrieveUpdateDestroyView(
    generics.RetrieveUpdateDestroyAPIView
):
    queryset = Supplier.objects.all().order_by("-created_at")
    serializer_class = SupplierSerializer
    permission_classes = [IsAuthenticated, IsAdmin]