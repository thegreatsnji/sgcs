"""URLs do módulo de utilizadores."""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    MyAccessHistoryView,
    MySessionsView,
    PasswordChangeView,
    PermissionListView,
    ProfileView,
    RoleViewSet,
    UserGroupViewSet,
    UserViewSet,
)

app_name = "users"

router = DefaultRouter()
router.register("accounts", UserViewSet, basename="user")
router.register("roles", RoleViewSet, basename="role")
router.register("groups", UserGroupViewSet, basename="group")

urlpatterns = [
    path("", include(router.urls)),
    path("permissions/", PermissionListView.as_view(), name="permissions"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path("profile/password/", PasswordChangeView.as_view(), name="password-change"),
    path("profile/sessions/", MySessionsView.as_view(), name="my-sessions"),
    path("profile/access-history/", MyAccessHistoryView.as_view(), name="access-history"),
]
