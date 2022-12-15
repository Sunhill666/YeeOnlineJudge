from django.urls import re_path

from contest.views.normal import ContestRetrieveView, ContestListView, ContestSubmitList, ContestRankList, \
    contest_verify

urlpatterns = [
    re_path(r'^contest/$', ContestListView.as_view()),
    re_path(r'^contest/verify/$', contest_verify),
    re_path(r'^contest/(?P<pk>\d+)/$', ContestRetrieveView.as_view()),
    re_path(r'^sub/(?P<pk>\d+)/$', ContestSubmitList.as_view()),
    re_path(r'^rank/(?P<pk>\d+)/$', ContestRankList.as_view())
]
