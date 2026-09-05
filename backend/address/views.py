from rest_framework import generics
from accounts.permissions import IsCustomer

from .models import Address
from .serializers import AddressSerializer


class AddressListCreateView(generics.ListCreateAPIView):

    serializer_class = AddressSerializer

    permission_classes = [IsCustomer]

    def get_queryset(self):
        return Address.objects.filter(
            customer=self.request.user
        )

    def perform_create(self, serializer):
        serializer.save(
            customer=self.request.user
        )


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):

    serializer_class = AddressSerializer

    permission_classes = [IsCustomer]

    def get_queryset(self):
        return Address.objects.filter(
            customer=self.request.user
        )
        
