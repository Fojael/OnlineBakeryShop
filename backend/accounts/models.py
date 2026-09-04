from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):

    # ==========================================================
    # EMAIL
    # ==========================================================

    email = models.EmailField(
        unique=True,
    )

    # ==========================================================
    # PHONE
    # ==========================================================

    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
    )

    # ==========================================================
    # ROLE
    # ==========================================================

    ROLE_CUSTOMER = "CUSTOMER"
    ROLE_ADMIN = "ADMIN"
    ROLE_SUPPLIER = "SUPPLIER"
    ROLE_DELIVERY = "DELIVERY"
    ROLE_DELIVERY_RIDER = "DELIVERY_RIDER"

    ROLE_CHOICES = [
        (ROLE_CUSTOMER, "Customer"),
        (ROLE_ADMIN, "Admin"),
        (ROLE_SUPPLIER, "Supplier"),
        (ROLE_DELIVERY_RIDER, "Delivery Rider"),
        (ROLE_DELIVERY, "Legacy Delivery Rider"),
    ]

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_CUSTOMER,
    )

    # ==========================================================
    # PROFILE IMAGE
    # ==========================================================

    profile_image = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True,
    )

    # ==========================================================
    # EMAIL LOGIN
    # ==========================================================

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = [
        "username",
    ]

    # ==========================================================
    # STRING REPRESENTATION
    # ==========================================================

    def __str__(self):

        return self.email

    # ==========================================================
    # ACCOUNT STATUS
    # ==========================================================

    is_email_verified = models.BooleanField(
        default=False,
    )

    # ==========================================================
    # TIMESTAMPS
    # ==========================================================

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    # ==========================================================
    # MODEL CONFIGURATION
    # ==========================================================

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "User"
        verbose_name_plural = "Users"

    # ==========================================================
    # HELPER PROPERTIES
    # ==========================================================

    @property
    def full_name(self):
        """
        Return full name if available,
        otherwise return username.
        """
        full_name = f"{self.first_name} {self.last_name}".strip()
        return full_name or self.username

    @property
    def image_url(self):
        """
        Return profile image URL or default image.
        """
        if self.profile_image:
            try:
                return self.profile_image.url
            except ValueError:
                pass

        return "/media/profiles/default.png"

    # ==========================================================
    # STRING REPRESENTATION
    # ==========================================================

    def __str__(self):
        return self.email
    
