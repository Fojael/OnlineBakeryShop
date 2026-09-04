from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):

    list_display = (
    "email",
    "username",
    "phone",
    "role",
    "is_active",
    "is_staff",
    "is_superuser",
)

    list_filter = (
        "role",
        "is_active",
        "is_staff",
        "is_superuser",
    )

    ordering = ("email",)

    fieldsets = UserAdmin.fieldsets + (
        (
            "Additional Information",
            {
                "fields": (
                    "phone",
                    "role",
                    "profile_image",
                )
            },
        ),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Additional Information",
            {
                "fields": (
                    "email",
                    "phone",
                    "role",
                )
            },
        ),
    )

    search_fields = (
        "email",
        "username",
    )
    
