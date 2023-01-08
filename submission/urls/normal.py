from django.urls import re_path

from submission.views.normal import SubmissionListCreateView, SubmissionRetrieveView, language_list

urlpatterns = [
    re_path(r'^submission/$', SubmissionListCreateView.as_view()),
    re_path(r'^submission/(?P<token>.+)/$', SubmissionRetrieveView.as_view()),
    re_path(r'^language/$', language_list)
]
