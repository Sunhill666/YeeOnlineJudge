from django.urls import re_path
from rest_framework import routers

from problem.views.admin import ProblemTagViewSet, TestCaseListCreateView, ProblemListCreateView, \
    ProblemRetrieveUpdateDestroyView, TestCaseDestroyView

router = routers.DefaultRouter()
router.register(r'tag', ProblemTagViewSet)

urlpatterns = [
    re_path(r'^test_case/$', TestCaseListCreateView.as_view()),
    re_path(r'^test_case/(?P<pk>\w+)/$', TestCaseDestroyView.as_view()),
    re_path(r'^problem/$', ProblemListCreateView.as_view()),
    re_path(r'^problem/(?P<pk>\d+)/$', ProblemRetrieveUpdateDestroyView.as_view()),
] + router.urls
