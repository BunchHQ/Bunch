from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

app_name = "bunch"

router = DefaultRouter()
router.register(r"", views.BunchViewSet, basename="bunch")

bunch_router = DefaultRouter()
bunch_router.register(r"channels", views.ChannelViewSet, basename="bunch-channel")
bunch_router.register(r"members", views.MemberViewSet, basename="bunch-member")

urlpatterns = [
    path("", include(router.urls)),
    path("<uuid:bunch_id>/", include(bunch_router.urls)),
]
