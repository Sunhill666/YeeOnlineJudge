from django.urls import re_path

from announcement.views.admin import AnnouncementListCreateView, AnnouncementRUDView

urlpatterns = [
    re_path(r'^$', AnnouncementListCreateView.as_view()),
    re_path(r'^(?P<pk>\d+)/$', AnnouncementRUDView.as_view()),
]
