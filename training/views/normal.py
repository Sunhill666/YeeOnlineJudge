from django.contrib.auth.hashers import check_password
from django.core.cache import cache
from rest_framework import generics, filters, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from submission.models import Submission
from submission.serializers import SubmissionListSerializers
from training.models import Training, TrainingRank, LearningPlan
from training.serializers import TrainingListSerializer, NormalDetailTrainingSerializer, \
    NormalDetailLearningPlanSerializer
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

    if training.password and not check_password(request.data.get('password'), training.password):
        return Response({"detail": "密码错误"}, status=status.HTTP_400_BAD_REQUEST)

    training_verify_set = cache.get('training_verify', set())
    training_verify_set.add(request.user.username)
    cache.set('training_verify', training_verify_set, None)
    return Response({"detail": "ok"}, status=status.HTTP_200_OK)


class ContestSubmitList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SubmissionListSerializers
    pagination_class = NumPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['start_time']

    def list(self, request, *args, **kwargs):
        contest_status = cache.get(request.user.username + '_contest', dict())
        if not contest_status.get(kwargs.get('pk'), False):
            return Response({"detail": "验证不通过，没有权限参加"}, status=status.HTTP_403_FORBIDDEN)
        queryset = self.filter_queryset(Submission.objects.filter(contest_id=kwargs.get('pk'))
                                        .order_by('-created_time'))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(instance=page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class ContestRankList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = NumPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['user']
    ordering_fields = ['commit_num', 'accepted_num', 'score']

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(TrainingRank.objects.filter(contest_id=kwargs.get('pk')).
                                        order_by('-score', '-accepted_num', 'commit_num'))
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(instance=page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
