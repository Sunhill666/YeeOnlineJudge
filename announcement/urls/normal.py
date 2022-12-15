from django.urls import re_path

from announcement.views.normal import AnnouncementListView, AnnouncementRetrieveView

urlpatterns = [
    re_path(r'^$', AnnouncementListView.as_view()),
    re_path(r'^(?P<pk>\d+)/$', AnnouncementRetrieveView.as_view(), name='announcement-detail'),
]
