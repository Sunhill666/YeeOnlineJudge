from rest_framework import routers

from problems.views.normal import ProblemViewSet, ProblemTagViewSet

router = routers.DefaultRouter()
router.register(r'problem', ProblemViewSet)
router.register(r'tag', ProblemTagViewSet)

urlpatterns = router.urls
