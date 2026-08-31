from rest_framework.permissions import BasePermission


# ==========================================================
# BASE ROLE PERMISSION
# ==========================================================

class RolePermission(
    BasePermission
):
    """
    Base permission class for
    role-based authorization.
    """

    allowed_roles = []

    def has_permission(
        self,
        request,
        view,
    ):

        user = request.user

        return (
            user.is_authenticated
            and getattr(
                user,
                "role",
                None,
            ) in self.allowed_roles
        )


# ==========================================================
# ADMIN
# ==========================================================

class IsAdmin(
    RolePermission
):

    allowed_roles = [
        "ADMIN",
    ]


# ==========================================================
# CUSTOMER
# ==========================================================

class IsCustomer(
    RolePermission
):

    allowed_roles = [
        "CUSTOMER",
    ]


# ==========================================================
# SUPPLIER
# ==========================================================

class IsSupplier(
    RolePermission
):

    allowed_roles = [
        "SUPPLIER",
    ]

    def has_permission(
        self,
        request,
        view,
    ):

        if not super().has_permission(
            request,
            view,
        ):

            return False

        supplier = getattr(
            request.user,
            "supplier",
            None,
        )

        return (
            supplier is not None
            and supplier.is_active
            and supplier.is_approved
        )


# ==========================================================
# DELIVERY RIDER
# ==========================================================

class IsDeliveryRider(
    RolePermission
):

    allowed_roles = [
        "DELIVERY",
    ]

    def has_permission(
        self,
        request,
        view,
    ):

        if not super().has_permission(
            request,
            view,
        ):
            return False

        user = request.user

        # Admin controls whether the rider can log in.
        if not user.is_active:
            return False

        return True