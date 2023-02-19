from django.urls import re_path

from organization import views
from organization.views.normal import UserRankList, UserRetrieveUpdateView, GroupRetrieveView

urlpatterns = [
    re_path(r'^rank/$', UserRankList.as_view()),
    re_path(r'^user/(?P<pk>\w+)/$', UserRetrieveUpdateView.as_view()),
    re_path(r'^group/(?P<pk>\d+)/$', GroupRetrieveView.as_view()),
    re_path(r'^register/$', views.normal.register),
]
