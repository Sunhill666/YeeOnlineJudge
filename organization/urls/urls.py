from django.urls import re_path
from organization.views import views

urlpatterns = [
    re_path(r'^user/?$', views.UserList.as_view(), name="user_all"),
    re_path(r'^user/<pk>?$', views.UserDetail.as_view(), name="user_detail"),
    re_path(r'^class/?$', views.ClassList.as_view(), name="class_all"),
    re_path(r'^class/<pk>?$', views.ClassDetail.as_view(), name="class_detail"),
]

