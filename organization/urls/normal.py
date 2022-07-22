from rest_framework import routers
from organization.views.normal import UserViewSet, ClassViewSet

router = routers.DefaultRouter()
router.register(r'user', UserViewSet)
router.register(r'class', ClassViewSet)

urlpatterns = router.urls
