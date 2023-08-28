from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/v1/", include("accounts.urls", namespace="accounts")),
    path("accounts/", include("allauth.urls")),
    path(
        "post/v1/",
        include("post.urls", namespace="post"),
    ),
    path(
        "community/v1/",
        include("community.urls", namespace="community"),
    ),
    path("pages/", include("pages.urls")),
    # API documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    # Optional UI:
    path(
        "",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]
urlpatterns = (
    urlpatterns
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
