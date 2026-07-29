from django.urls import path
from .views import ProfileView, RegisterView
from .views import RegisterView, LoginView
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LogoutView
from .views import ChangePasswordView
from .views import AdminDashboardView


urlpatterns = [
    path("register/", RegisterView.as_view()),
    
    path("login/", LoginView.as_view()),
    path(
    "profile/",
    ProfileView.as_view(),
),

    path(
        "refresh/",
        TokenRefreshView.as_view(),
        name="token_refresh"
    ),
    path(
        "logout/",
        LogoutView.as_view(),
        name="auth_logout"
    ),
    path(
        "change-password/",
        ChangePasswordView.as_view(),
        name="change_password"
    ),
    path(
    "admin-dashboard/",
    AdminDashboardView.as_view(),
    name="admin_dashboard"
),
 
]