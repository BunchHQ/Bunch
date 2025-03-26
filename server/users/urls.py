from rest_framework import routers

from users.views import UserViewSet

app_name = "users"

router = routers.DefaultRouter()
router.register(r"user", UserViewSet, basename="user")
# unload groups for now
# router.register(r"group", GroupViewSet, basename='group')
