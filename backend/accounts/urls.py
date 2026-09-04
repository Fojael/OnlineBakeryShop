from django.urls import path
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)

from .views import (
    RegisterView,
    LoginView,
    ProfileView,
    ChangePasswordView,
    LogoutView,
    AdminDashboardView,
)

app_name = "accounts"

urlpatterns = [

    # ==========================================================
    # Authentication
    # ==========================================================

    path(
        "register/",
        RegisterView.as_view(),
        name="register",
    ),

    path(
        "login/",
        LoginView.as_view(),
        name="login",
    ),

    path(
        "logout/",
        LogoutView.as_view(),
        name="logout",
    ),

    # ==========================================================
    # JWT
    # ==========================================================

    path(
        "refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh",
    ),

    path(
        "verify/",
        TokenVerifyView.as_view(),
        name="token_verify",
    ),

    # ==========================================================
    # User Profile
    # ==========================================================

    path(
        "profile/",
        ProfileView.as_view(),
        name="profile",
    ),

    path(
        "change-password/",
        ChangePasswordView.as_view(),
        name="change_password",
    ),

    # ==========================================================
    # Admin
    # ==========================================================

    path(
        "admin-dashboard/",
        AdminDashboardView.as_view(),
        name="admin_dashboard",
    ),
]

