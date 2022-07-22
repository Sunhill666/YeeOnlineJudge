from rest_framework import viewsets

from problems.models import Problem, ProblemTag
from problems.serializers import ProblemSerializers, ProblemTagSerializers
from problems.pagination import ProblemNumPagination


class ProblemViewSet(viewsets.ModelViewSet):
    serializer_class = ProblemSerializers
    queryset = Problem.objects.all()
    pagination_class = ProblemNumPagination


class ProblemTagViewSet(viewsets.ModelViewSet):
    serializer_class = ProblemTagSerializers
    queryset = ProblemTag.objects.all()
