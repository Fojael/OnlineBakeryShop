from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .models import Address
from .serializers import AddressSerializer


class AddressListCreateView(generics.ListCreateAPIView):

    serializer_class = AddressSerializer

    permission_classes = [IsAuthenticated]

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

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Address.objects.filter(
            customer=self.request.user
        )
        
