from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    # ==========================================================
    # USER ROLES
    # ==========================================================

    ROLE_CHOICES = (
        ("ADMIN", "Admin"),
        ("CUSTOMER", "Customer"),
        ("SUPPLIER", "Supplier"),
        ("DELIVERY", "Delivery Rider"),
    )

    # ==========================================================
    # AUTHENTICATION
    # ==========================================================

    email = models.EmailField(
        unique=True,
        db_index=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    # ==========================================================
    # PROFILE
    # ==========================================================

    phone = models.CharField(
        max_length=20,
        blank=True,
    )

    profile_image = models.ImageField(
        upload_to="profiles/",
        default="profiles/default.png",
        blank=True,
        null=True,
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="CUSTOMER",
        db_index=True,
    )

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