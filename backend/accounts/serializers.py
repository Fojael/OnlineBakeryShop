from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password

from rest_framework import serializers

from .models import User


# ==========================================================
# REGISTER SERIALIZER
# ==========================================================

class RegisterSerializer(
    serializers.ModelSerializer
):

    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={
            "input_type": "password"
        },
    )

    class Meta:

        model = User

        fields = [
            "id",
            "username",
            "email",
            "phone",
            "password",
        ]

        read_only_fields = [
            "id",
        ]

    # ======================================================
    # CREATE USER
    # ======================================================

    def create(
        self,
        validated_data,
    ):

        password = validated_data.pop(
            "password"
        )

        user = User(
            role=User.ROLE_CUSTOMER,
            **validated_data,
        )

        user.set_password(
            password
        )

        user.save()

        return user


# ==========================================================
# LOGIN SERIALIZER
# ==========================================================

class LoginSerializer(
    serializers.Serializer
):

    email = serializers.EmailField(
        required=True,
    )

    password = serializers.CharField(
        write_only=True,
        required=True,
        style={
            "input_type": "password"
        },
    )

    def validate(
        self,
        attrs,
    ):

        email = attrs.get(
            "email"
        )

        password = attrs.get(
            "password"
        )

        # ==================================================
        # FIND USER
        # ==================================================

        try:

            user = User.objects.get(
                email__iexact=email
            )

        except User.DoesNotExist:

            raise serializers.ValidationError(
                "Invalid email or password."
            )

        # ==================================================
        # CHECK PASSWORD
        # ==================================================

        if not user.check_password(
            password
        ):

            raise serializers.ValidationError(
                "Invalid email or password."
            )

        # ==================================================
        # CHECK ACTIVE
        # ==================================================

        if not user.is_active:

            raise serializers.ValidationError(
                "This account is inactive."
            )

        attrs["user"] = user

        return attrs


# ==========================================================
# PROFILE SERIALIZER
# ==========================================================

class UserSerializer(
    serializers.ModelSerializer
):

    profile_image = serializers.ImageField(
        required=False,
        allow_null=True,
    )

    class Meta:

        model = User

        fields = [
            "id",
            "username",
            "email",
            "phone",
            "role",
            "profile_image",
        ]

        read_only_fields = [
            "id",
            "role",
        ]


# ==========================================================
# CHANGE PASSWORD SERIALIZER
# ==========================================================

class ChangePasswordSerializer(
    serializers.Serializer
):

    old_password = serializers.CharField(
        write_only=True,
        style={
            "input_type": "password"
        },
    )

    new_password = serializers.CharField(
        write_only=True,
        validators=[
            validate_password
        ],
        style={
            "input_type": "password"
        },
    )

    confirm_password = serializers.CharField(
        write_only=True,
        style={
            "input_type": "password"
        },
    )

    def validate(
        self,
        attrs,
    ):

        if (
            attrs["new_password"]
            != attrs["confirm_password"]
        ):

            raise serializers.ValidationError(
                {
                    "confirm_password":
                    "Passwords do not match."
                }
            )

        return attrs