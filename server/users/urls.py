from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import UserViewSet

router = DefaultRouter()
router.register(r"", UserViewSet, basename="user")
# groups not needed rn
# router.register(r"group", GroupViewSet, basename="group")

urlpatterns = [
    path("", include(router.urls)),
]
