from rest_framework import status, permissions, filters, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from YeeOnlineJudge.tasks import to_judge
from problem.models import Problem
from submission.models import Submission
from submission.serializers import BaseSubmissionSerializers, SubmissionListSerializers
from training.models import TrainingRank
from utils.judger import submission
from utils.pagination import NumPagination
from utils.tools import get_languages, prase_template, default_statistics


class SubmissionListCreateView(generics.ListCreateAPIView):
    queryset = Submission.objects.filter(training__isnull=True).order_by('-created_time')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = NumPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['created_by__username', 'problem__title']
    ordering_fields = ['created_time']

    def get_serializer_class(self):
        if self.request.method == "GET":
            return SubmissionListSerializers
        return BaseSubmissionSerializers

    def create(self, request, *args, **kwargs):
        # 如果问题中有template存在且提交的语言为template支持的语言，则把提交的代码与template结合起来提交
        if template := Problem.objects.get(pk=request.data.get('problem')).template:
            if request.data.get('language_id') in [int(i) for i in template.keys()]:
                prased = prase_template(template.get(str(request.data.get('language_id'))))
                request.data.update({
                    "code": f"{prased.get('prepend')}\n{request.data.get('code')}\n{prased.get('append')}"
                })

        if x_forwarded_for := request.META.get('HTTP_X_FORWARDED_FOR'):
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        if request.data.get('stdin'):
            expected_output = request.data.get('expected_output')
            problem = Problem.objects.get(pk=request.data.get('problem'))
            sub = submission.submit(
                source_code=bytes(request.data.get('code'), 'utf-8'),
                language=request.data.get('language_id'),
                stdin=bytes(request.data.get('stdin'), 'utf-8'),
                expected_output=None if not expected_output else bytes(expected_output, 'utf-8'),
                cpu_time_limit=problem.time_limit / 1000,
                memory_limit=problem.memory_limit * 1024,
                wait=True
            )
            return Response(sub, status=status.HTTP_200_OK)
        else:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            submit = serializer.save(created_by=request.user, status=Submission.Status.IQ, submit_ip=ip)
            headers = self.get_success_headers(serializer.data)
            to_judge.delay(
                code=request.data.get('code'),
                language_id=request.data.get('language_id'),
                problem_id=request.data.get('problem'),
                submission_id=submit.id,
                training=request.data.get('training')
            )

        if training := request.data.get('training'):
            try:
                TrainingRank.objects.get(user=request.user, training_id=training)
            except TrainingRank.DoesNotExist:
                TrainingRank.objects.create(user=request.user, training_id=training,
                                            statistics={
                                                "statistics": default_statistics(),
                                                "score": 0
                                            })

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class SubmissionRetrieveView(generics.RetrieveAPIView):
    queryset = Submission.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = BaseSubmissionSerializers


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def language_list(request):
    return Response(get_languages(), status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def get_submit_details(request, token):
    return Response(submission.get(token), status=status.HTTP_200_OK)
