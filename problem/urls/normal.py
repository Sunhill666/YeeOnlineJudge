from django.urls import re_path

from problem.views.normal import ProblemListView, ProblemRetrieveView, ProblemTagListView, ProblemTagRetrieveView

urlpatterns = [
    re_path(r'^problem/$', ProblemListView.as_view()),
    re_path(r'^problem/(?P<pk>\d+)/$', ProblemRetrieveView.as_view()),
    re_path(r'^tag/$', ProblemTagListView.as_view()),
    re_path(r'^tag/(?P<pk>\w+)/$', ProblemTagRetrieveView.as_view()),
]
