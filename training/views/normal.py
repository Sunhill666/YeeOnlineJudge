from django.contrib.auth.hashers import check_password
from django.core.cache import cache
from django.db.models import Case, Count, When
from django.utils import timezone
from rest_framework import generics, filters, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from submission.models import Submission
from submission.serializers import SubmissionListSerializers
from training.models import Training, TrainingRank, LearningPlan
from training.serializers import TrainingListSerializer, NormalDetailTrainingSerializer, \
    NormalDetailLearningPlanSerializer, BaseContestRankSerializer
from utils.pagination import NumPagination


class ContestListView(generics.ListAPIView):
    queryset = Training.objects.filter(start_time__lt=timezone.now()).order_by('-start_time')
    serializer_class = TrainingListSerializer
    pagination_class = NumPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['start_time']


class ContestRetrieveView(generics.RetrieveAPIView):
    queryset = Training.objects.filter(start_time__lt=timezone.now())
    serializer_class = NormalDetailTrainingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


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


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def training_verify(request):
    try:
        if not request.data.get('id'):
            return Response({"detail": "id为空"}, status=status.HTTP_400_BAD_REQUEST)

        training = Training.objects.get(pk=request.data.get('id'))
    except Training.DoesNotExist:
        return Response({"detail": "比赛不存在"}, status=status.HTTP_404_NOT_FOUND)

    training_verify_set = cache.get('training_verify_' + str(request.data.get('id')), set())

    if request.data.get('password') and \
            training.password and \
            check_password(request.data.get('password'), training.password):
        training_verify_set.add(request.user.username)
        cache.set('training_verify_' + str(request.data.get('id')), training_verify_set, None)
        return Response({"detail": "ok"}, status=status.HTTP_200_OK)

    # 无密码使用身份认证参加，如登录用户在比赛所允许的用户或组内，即可认证成功
    user_group = request.user.profile.group
    if training.user.contains(request.user) or training.group.contains(user_group):
        training_verify_set.add(request.user.username)
        cache.set('training_verify_' + str(request.data.get('id')), training_verify_set, None)
        return Response({"detail": "ok"}, status=status.HTTP_200_OK)
    else:
        return Response({"detail": "failed"}, status=status.HTTP_403_FORBIDDEN)


class ContestSubmitList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubmissionListSerializers
    pagination_class = NumPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['created_by__username', 'problem__title']
    ordering_fields = ['created_time']

    def list(self, request, *args, **kwargs):
        training_verify_set = cache.get('training_verify_' + str(kwargs.get('pk')), set())
        if request.user.username not in training_verify_set and request.user.profile.group.name != "管理组":
            return Response({"detail": "验证不通过，没有权限"}, status=status.HTTP_403_FORBIDDEN)
        queryset = self.filter_queryset(queryset = Submission.objects.filter(training_id=kwargs.get('pk')).annotate(
            sticky_top=Count(Case(When(status="Processing", then=1)))
            ).order_by("-sticky_top", "-created_time"))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(instance=page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ContestRankList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BaseContestRankSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["statistics__score", "statistics__statistics__Accepted", "statistics__statistics__Commit"]

    def list(self, request, *args, **kwargs):
        training_verify_set = cache.get('training_verify_' + str(kwargs.get('pk')), set())
        if request.user.username not in training_verify_set and request.user.profile.group.name != "管理组":
            return Response({"detail": "验证不通过，没有权限"}, status=status.HTTP_403_FORBIDDEN)
        queryset = self.filter_queryset(
            TrainingRank.objects.filter(training_id=kwargs.get('pk')).
            order_by(
                "-statistics__score",
                "-statistics__statistics__Accepted",
                "statistics__statistics__Commit"
            )
        )
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
