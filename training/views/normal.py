from django.contrib.auth.hashers import check_password
from django.core.cache import cache
from django.core.exceptions import ObjectDoesNotExist
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
    queryset = Training.objects.filter(is_open=True)
    serializer_class = TrainingListSerializer
    pagination_class = NumPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['start_time']


class ContestRetrieveView(generics.RetrieveAPIView):
    queryset = Training.objects.filter(is_open=True)
    serializer_class = NormalDetailTrainingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class LearningPlanListView(generics.ListAPIView):
    queryset = LearningPlan.objects.filter(is_open=True)
    serializer_class = NormalDetailLearningPlanSerializer
    pagination_class = NumPagination
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['created_time']


class LearningPlanRetrieveView(generics.RetrieveAPIView):
    queryset = LearningPlan.objects.filter(is_open=True)
    serializer_class = NormalDetailLearningPlanSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def training_verify(request):
    try:
        if not request.data.get('id'):
            return Response({"detail": "id为空"}, status=status.HTTP_400_BAD_REQUEST)

        training = Training.objects.filter(is_open=True).get(pk=request.data.get('id'))
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
    try:
        user_group = request.user.profile.group
        if training.user.get(username=request.user.username) or training.group.get(pk=user_group.id):
            training_verify_set.add(request.user.username)
            cache.set('training_verify_' + str(request.data.get('id')), training_verify_set, None)
            return Response({"detail": "ok"}, status=status.HTTP_200_OK)
    except ObjectDoesNotExist:
        return Response({"detail": "failed"}, status=status.HTTP_403_FORBIDDEN)


class ContestSubmitList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubmissionListSerializers
    pagination_class = NumPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['start_time']

    def list(self, request, *args, **kwargs):
        training_verify_set = cache.get('training_verify_' + str(kwargs.get('pk')), set())
        if request.user.username not in training_verify_set:
            return Response({"detail": "验证不通过，没有权限"}, status=status.HTTP_403_FORBIDDEN)
        queryset = self.filter_queryset(Submission.objects.filter(training_id=kwargs.get('pk'))
                                        .order_by('-created_time'))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(instance=page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ContestRankList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BaseContestRankSerializer
    pagination_class = NumPagination
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["statistics__score", "statistics__statistics__Accepted", "statistics__statistics__Commit"]

    def list(self, request, *args, **kwargs):
        training_verify_set = cache.get('training_verify_' + str(kwargs.get('pk')), set())
        if request.user.username not in training_verify_set:
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
            serializer = self.get_serializer(instance=page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
