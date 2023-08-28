from rest_framework.routers import DefaultRouter
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from . import views

router = DefaultRouter()

router.register("users", views.UserViewSet, basename="users")
router.register("register", views.RegisterViewSet, basename="register")
router.register("user-followership", views.UserFollowshipViewset, basename="user-followership")
router.register("user-privacy", views.UpdateUserPrivacyViewset, basename="user-privacy")

app_name = "accounts"

urlpatterns = [
    path("", include(router.urls)),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("update-profile", views.UpdateProfileView.as_view(), name="update-profile"),
    path("update-cover-image", views.UpdateCoverImageView.as_view(), name="update-cover-image"),
    path("update-profile-image", views.UpdateProfileImageView.as_view(), name="update-profile-image")


]
