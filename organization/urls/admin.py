from django.urls import re_path
from rest_framework import routers

from organization.views.admin import GroupViewSet, UserListCreateView, UserRetrieveUpdateDestroyView, batch_register

router = routers.DefaultRouter()

router.register(r'group', GroupViewSet)

urlpatterns = [
    re_path(r'^user/$', UserListCreateView.as_view()),
    re_path(r'^userbatch/$', batch_register),
    re_path(r'^user/(?P<pk>\d+)/$', UserRetrieveUpdateDestroyView.as_view()),
] + router.urls
