from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView

from problems.models import Problem, ProblemTag
from problems.pagination import ProblemNumPagination
from problems.serializers import ProblemSerializers, ProblemTagSerializers
from utils.tools import get_random_string


class ProblemViewSet(viewsets.ModelViewSet):
    serializer_class = ProblemSerializers
    queryset = Problem.objects.all()
    pagination_class = ProblemNumPagination


class ProblemTagViewSet(viewsets.ModelViewSet):
    serializer_class = ProblemTagSerializers
    queryset = ProblemTag.objects.all()


class TestCasePost(APIView):
    def post(self, request):
        test_case = request.data.get('test_case')
        if not test_case:
            return Response("测试用例上传失败", status=status.HTTP_400_BAD_REQUEST)

        test_case_id = get_random_string()

        filename = test_case_id + ".zip"



        with open(filename, "wb") as f:
            for chunk in test_case.chunks():
                f.write(chunk)
