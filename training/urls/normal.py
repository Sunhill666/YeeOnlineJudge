from django.urls import re_path

from training.views.normal import ContestRetrieveView, ContestListView, ContestSubmitList, ContestRankList, \
    LearningPlanListView, LearningPlanRetrieveView

urlpatterns = [
    re_path(r'^training/$', ContestListView.as_view()),
    re_path(r'^plan/$', LearningPlanListView.as_view()),
    re_path(r'^plan/(?P<pk>\d+)/$', LearningPlanRetrieveView.as_view()),
    re_path(r'^training/(?P<pk>\d+)/$', ContestRetrieveView.as_view()),
    re_path(r'^sub/(?P<pk>\d+)/$', ContestSubmitList.as_view()),
    re_path(r'^rank/(?P<pk>\d+)/$', ContestRankList.as_view())
]
