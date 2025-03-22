from rest_framework import routers

from users.views import GroupViewSet, UserViewSet

router = routers.DefaultRouter()
router.register(r"user", UserViewSet, basename='user')
router.register(r"group", GroupViewSet, basename='group')
