from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

app_name = "community"

router = DefaultRouter()

router.register("groups", views.GroupViewSet, basename="groups") 

urlpatterns = [
    path("", include(router.urls)),
]
