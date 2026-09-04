from rest_framework import serializers

from .models import Address


class AddressSerializer(serializers.ModelSerializer):

    class Meta:
        model = Address

        fields = [
            "id",
            "full_name",
            "phone",
            "division",
            "district",
            "upazila",
            "address_line",
            "postal_code",
            "is_default",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]
        
