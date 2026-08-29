from django.contrib.auth.password_validation import (
    validate_password,
)

from rest_framework import serializers

from accounts.models import User

from .models import Supplier


# ==========================================================
# SUPPLIER
# ==========================================================

class SupplierSerializer(serializers.ModelSerializer):

    class Meta:

        model = Supplier

        fields = "__all__"


# ==========================================================
# SUPPLIER REGISTER
# ==========================================================

class SupplierRegisterSerializer(
    serializers.ModelSerializer
):

    username = serializers.CharField()

    password = serializers.CharField(
        write_only=True,
        validators=[
            validate_password,
        ],
        style={
            "input_type": "password",
        },
    )

    confirm_password = serializers.CharField(
        write_only=True,
        style={
            "input_type": "password",
        },
    )

    class Meta:

        model = Supplier

        fields = [
            "username",
            "password",
            "confirm_password",
            "name",
            "company",
            "email",
            "phone",
            "address",
        ]

    def validate(self, attrs):

        if (
            attrs["password"]
            != attrs["confirm_password"]
        ):
            raise serializers.ValidationError(
                {
                    "confirm_password":
                    "Passwords do not match."
                }
            )

        if User.objects.filter(
            email=attrs["email"]
        ).exists():

            raise serializers.ValidationError(
                {
                    "email":
                    "This email is already registered."
                }
            )

        if User.objects.filter(
            username=attrs["username"]
        ).exists():

            raise serializers.ValidationError(
                {
                    "username":
                    "This username is already taken."
                }
            )

        return attrs

    def create(
        self,
        validated_data,
    ):

        username = validated_data.pop(
            "username"
        )

        password = validated_data.pop(
            "password"
        )

        validated_data.pop(
            "confirm_password"
        )

        email = validated_data.get(
            "email"
        )

        user = User.objects.create(
            username=username,
            email=email,
            role="SUPPLIER",
            is_active=False,
        )

        user.set_password(
            password
        )

        user.save()

        supplier = Supplier.objects.create(
            user=user,
            **validated_data,
        )

        return supplier