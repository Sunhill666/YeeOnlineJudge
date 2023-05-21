from django.contrib.auth.models import AnonymousUser
from django.db.models import Case, Count, When, Q
from django.utils import timezone
from rest_framework import generics, filters

from organization import permissions
from submission.models import Submission
from submission.serializers import SubmissionListSerializers
from training.models import Training, TrainingRank, LearningPlan
from training.serializers import TrainingListSerializer, NormalDetailTrainingSerializer, \
    NormalDetailLearningPlanSerializer, BaseContestRankSerializer
from utils.pagination import NumPagination


class ContestListView(generics.ListAPIView):
    serializer_class = TrainingListSerializer
    pagination_class = NumPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['start_time']

    def get_queryset(self):
        if isinstance(self.request.user, AnonymousUser):
            username = -1
            group = -1
        elif self.request.user.profile.group.name == "管理组":
            return Training.objects.all()
        else:
            username = self.request.user.username
            group = self.request.user.profile.group.id
        return Training.objects.filter(
            Q(start_time__lt=timezone.now()) & 
            Q(
                Q(Q(user=None) & Q(group=None)) |
                Q(Q(user=username) | Q(group=group))
            )
        ).order_by('-start_time')


class ContestRetrieveView(generics.RetrieveAPIView):
    queryset = Training.objects.filter(start_time__lt=timezone.now())
    serializer_class = NormalDetailTrainingSerializer
    permission_classes = [permissions.IsAuthenticated & permissions.CanJoinTraining]

    def get_queryset(self):
        if isinstance(self.request.user, AnonymousUser):
            username = -1
            group = -1
        elif self.request.user.profile.group.name == "管理组":
            return Training.objects.all()
        else:
            username = self.request.user.username
            group = self.request.user.profile.group.id
        return Training.objects.filter(
            Q(start_time__lt=timezone.now()) & 
            Q(
                Q(Q(user=None) & Q(group=None)) |
                Q(Q(user=username) | Q(group=group))
            )
        ).order_by('-start_time')


class LearningPlanListView(generics.ListAPIView):
    queryset = LearningPlan.objects.all()
    serializer_class = NormalDetailLearningPlanSerializer
    pagination_class = NumPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['created_time']


class LearningPlanRetrieveView(generics.RetrieveAPIView):
    queryset = LearningPlan.objects.all()
    serializer_class = NormalDetailLearningPlanSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class ContestSubmitList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated & permissions.CanJoinTraining]
    serializer_class = SubmissionListSerializers
    pagination_class = NumPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['created_by__username', 'problem__title']
    ordering_fields = ['created_time']

    def get_queryset(self):
        queryset = Submission.objects.filter(
            training_id=self.kwargs.get('pk')
        ).annotate(
            sticky_top=Count(Case(When(status="Processing", then=1)))
        ).order_by("-sticky_top", "-created_time")
        return queryset


class ContestRankList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated & permissions.CanJoinTraining]
    serializer_class = BaseContestRankSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["statistics__score", "statistics__statistics__Accepted", "statistics__statistics__Commit"]

    def get_queryset(self):
        queryset = TrainingRank.objects.filter(
            training_id=self.kwargs.get('pk')
        ).order_by(
            "-statistics__score",
            "-statistics__statistics__Accepted",
            "statistics__statistics__Commit"
        )
        return queryset
