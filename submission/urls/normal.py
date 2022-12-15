from django.urls import re_path

from submission.views.normal import SubmissionView, SubmissionRetrieveView, language_list

urlpatterns = [
    re_path('^$', SubmissionView.as_view()),
    re_path(r'^language/$', language_list),
    re_path(r'^(?P<token>.+)/$', SubmissionRetrieveView.as_view())
]
