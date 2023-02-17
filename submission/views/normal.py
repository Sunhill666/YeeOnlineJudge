from rest_framework import status, permissions, filters, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from YeeOnlineJudge.tasks import to_judge
from problem.models import Problem
from submission.models import Submission
from submission.serializers import BaseSubmissionSerializers
from training.models import TrainingRank
from utils.judger import submission
from utils.pagination import NumPagination
from utils.tools import get_languages


class SubmissionListCreateView(generics.ListCreateAPIView):
    queryset = Submission.objects.all().order_by('id')
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    pagination_class = NumPagination
    serializer_class = BaseSubmissionSerializers
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['created_by__username', 'problem__title']
    ordering_fields = ['created_time']

    def create(self, request, *args, **kwargs):
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
            submit = serializer.save(created_by=request.user, status=Submission.Status.IQ)
            headers = self.get_success_headers(serializer.data)
            to_judge.delay(
                code=request.data.get('code'),
                language_id=request.data.get('language_id'),
                problem_id=request.data.get('problem'),
                submission_id=submit.id,
                training=request.data.get('training')
            )

        if training := request.data.get('training'):
            TrainingRank.objects.create(user=request.user, training=training)

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class SubmissionRetrieveView(generics.RetrieveAPIView):
    queryset = Submission.objects.all()
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = BaseSubmissionSerializers

    def retrieve(self, request, *args, **kwargs):
        return Response()


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def language_list(request):
    return Response(get_languages(), status=status.HTTP_200_OK)
