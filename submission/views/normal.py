from datetime import datetime

from django.core.cache import cache
from django.db.models import Q
from rest_framework import status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from YeeOnlineJudge.task import process_status, contest_rank, process_statistics
from organization.models import UserProfile
from problem.models import Problem
from submission.models import Submission
from submission.serializers import SubmissionSerializers
from training.models import Training, TrainingRank
from utils.judger import submission
from utils.judger.languages import languages
from utils.pagination import NumPagination
from utils.tools import read_test_case, get_judge_client


def test_judge(request, judge_client, problem):
    expected_output = None
    stdin = request.data.get("stdin")
    if request.data.get("expected_output", None):
        expected_output = request.data.get("expected_output")

    return submission.submit(
        judge_client,
        source_code=bytes(request.data.get("code"), 'utf-8'),
        language=request.data.get("language_id"),
        stdin=bytes(stdin, 'utf-8'),
        expected_output=None if not expected_output else bytes(expected_output, 'utf-8'),
        cpu_time_limit=problem.time_limit / 1000,
        memory_limit=problem.memory_limit * 1024,
        wait=True
    )


def normal_judge(request, judge_client, problem):
    stdin_list, expected_output_list = read_test_case(problem.test_case.path)
    stdin = ''.join(stdin_list)
    expected_output = ''.join(expected_output_list)

    return submission.submit(
        judge_client,
        source_code=bytes(request.data.get("code"), 'utf-8'),
        language=request.data.get("language_id"),
        stdin=bytes(stdin, 'utf-8'),
        expected_output=None if not expected_output else bytes(expected_output, 'utf-8'),
        cpu_time_limit=problem.time_limit / 1000,
        memory_limit=problem.memory_limit * 1024
    )


class SubmissionView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['commit_by__username', 'problem__title']
    ordering_fields = ['created_time']

    def filter_queryset(self, queryset):
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset

    def get(self, request):
        page = NumPagination()
        submissions = self.filter_queryset(Submission.objects.filter(contest_id__isnull=True).order_by('-created_time'))
        page_sub = page.paginate_queryset(queryset=submissions, request=request, view=self)
        serializer = SubmissionSerializers(page_sub, many=True)
        return page.get_paginated_response(serializer.data)

    def post(self, request):
        judge_client = get_judge_client()

        try:
            problem = Problem.objects.get(pk=request.data.get("problem"))
        except Problem.DoesNotExist:
            return Response({"detail": "题目不存在"}, status=status.HTTP_404_NOT_FOUND)

        if training_id := request.data.get('training', None):
            try:
                training = Training.objects.get(pk=training_id)
            except Training.DoesNotExist:
                return Response({"detail": "比赛不存在"}, status=status.HTTP_404_NOT_FOUND)

            if datetime.now() > training.end_time:
                return Response({"detail": "比赛已过期"}, status=status.HTTP_403_FORBIDDEN)
            if datetime.now() < training.start_time:
                return Response({"detail": "比赛未开始"}, status=status.HTTP_403_FORBIDDEN)
            if problem.id not in [int(i) for i in training.score.keys()]:
                return Response({"detail": "题目不存在"}, status=status.HTTP_403_FORBIDDEN)

            contestper = cache.get(request.user.username + '_contest', dict())
            if not contestper.get(str(training_id), False):
                return Response({"detail": "没有参加权限"}, status=status.HTTP_403_FORBIDDEN)

        # 请求不带stdin则为测试判题不保存该提交，否则保存
        if request.data.get("stdin", None):
            sub = test_judge(request, judge_client, problem)
            sub.load(judge_client)
            return Response(sub, status=status.HTTP_200_OK)
        else:
            sub = normal_judge(request, judge_client, problem)
            sub.load(judge_client)
            request.data['token'] = sub.token
            request.data['status'] = sub.status

        serializer = SubmissionSerializers(data=request.data)
        if serializer.is_valid():
            serializer.save(commit_by=request.user)
            process_status.delay(sub.token)
            if training_id := request.data.get('training', None):
                contest_rank.delay(sub.token, training_id)
                user_rank = TrainingRank.objects.get(Q(training_id=training_id) & Q(user=request.user))
                user_rank.commit_num = len(Submission.objects.filter(Q(commit_by=request.user) &
                                                                     Q(training_id=training_id)))
                user_rank.save()
            else:
                process_statistics.delay(sub.token)
                user_profile = UserProfile.objects.get(user=request.user)
                user_profile.commit_num = len(
                    Submission.objects.filter(Q(commit_by=request.user) & Q(contest_id__isnull=True)))
                problem.commit_num = len(Submission.objects.filter(Q(problem=problem) & Q(contest_id__isnull=True)))
                user_profile.save()
                problem.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubmissionRetrieveView(APIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get(self, request, token):
        try:
            sub = Submission.objects.get(pk=token)
        except Submission.DoesNotExist:
            return Response({"detail": "未找到该提交"}, status=status.HTTP_404_NOT_FOUND)

        judge_client = get_judge_client()
        sub = submission.get(judge_client, sub.token)
        sub.status = sub.status.get("id")
        return Response(sub, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def language_list(request):
    if request.method == "GET":
        return Response(languages, status=status.HTTP_200_OK)
