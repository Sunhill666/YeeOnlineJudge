from django.urls import re_path

from contest.views.admin import ContestListCreateView, ContestRetrieveUpdateDestroyView, ProblemSetListCreateView, \
    ProblemSetRetrieveUpdateDestroy

urlpatterns = [
    re_path(r'^contest/$', ContestListCreateView.as_view()),
    re_path(r'^contest/(?P<pk>\d+)/$', ContestRetrieveUpdateDestroyView.as_view()),
    re_path(r'^problem_set/$', ProblemSetListCreateView.as_view()),
    re_path(r'^problem_set/(?P<pk>\d+)/$', ProblemSetRetrieveUpdateDestroy.as_view()),
]
