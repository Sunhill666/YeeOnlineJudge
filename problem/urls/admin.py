from django.urls import re_path
from rest_framework import routers

from problem.views.admin import PictureDestroyView, PictureListCreateView, ProblemTagViewSet, \
    TestCaseListCreateView, ProblemListCreateView, \
    ProblemRetrieveUpdateDestroyView, TestCaseDestroyView, special_problem_list

router = routers.DefaultRouter()
router.register(r'tag', ProblemTagViewSet)

urlpatterns = [
    re_path(r'^test_case/$', TestCaseListCreateView.as_view()),
    re_path(r'^test_case/(?P<pk>\w+)/$', TestCaseDestroyView.as_view()),
    re_path(r'^pic/$', PictureListCreateView.as_view()),
    re_path(r'^pic/(?P<pk>\w+)/$', PictureDestroyView.as_view()),
    re_path(r'^problem/all/$', special_problem_list),
    re_path(r'^problem/$', ProblemListCreateView.as_view()),
    re_path(r'^problem/(?P<pk>\d+)/$', ProblemRetrieveUpdateDestroyView.as_view()),
] + router.urls
