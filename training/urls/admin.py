from django.urls import re_path
from rest_framework import routers

from training.views.admin import TrainingListCreateView, TrainingRetrieveUpdateDestroyView, ProblemSetViewSet, \
    LearningPlanListCreateView, LearningPlanRetrieveUpdateDestroyView

router = routers.DefaultRouter()
router.register(r'problem_set', ProblemSetViewSet)

urlpatterns = [
    re_path(r'^training/$', TrainingListCreateView.as_view()),
    re_path(r'^training/(?P<pk>\d+)/$', TrainingRetrieveUpdateDestroyView.as_view()),
    re_path(r'^plan/$', LearningPlanListCreateView.as_view()),
    re_path(r'^plan/(?P<pk>\d+)/$', LearningPlanRetrieveUpdateDestroyView.as_view()),
] + router.urls
