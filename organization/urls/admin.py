from django.urls import re_path
from rest_framework import routers

from organization.views.admin import GroupViewSet, UserListCreateView, UserRetrieveUpdateDestroyView, batch_register, special_group_list, special_user_list

router = routers.DefaultRouter()

router.register(r'group', GroupViewSet)

urlpatterns = [
    re_path(r'^user/$', UserListCreateView.as_view()),
    re_path(r'^userbatch/$', batch_register),
    re_path(r'^user/all/$', special_user_list),
    re_path(r'^user/(?P<pk>\w+)/$', UserRetrieveUpdateDestroyView.as_view()),
    re_path(r'^group/all/$', special_group_list),
] + router.urls
