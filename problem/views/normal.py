from rest_framework import generics, filters, permissions

from problem.models import Problem, ProblemTag
from problem.serializers import ProblemListSerializer, NormalProblemTagSerializer, NormalProblemSerializer
from utils.pagination import NumPagination


class ProblemListView(generics.ListAPIView):
    queryset = Problem.objects.filter(is_public=True)
    pagination_class = NumPagination
    permission_classes = [permissions.AllowAny]
    serializer_class = ProblemListSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['=difficulty', 'title', 'tags__tag_name']


class ProblemRetrieveView(generics.RetrieveAPIView):
    queryset = Problem.objects.filter(is_public=True)
    serializer_class = NormalProblemSerializer
    permission_classes = [permissions.AllowAny]


class ProblemTagListView(generics.ListAPIView):
    queryset = ProblemTag.objects.all()
    serializer_class = NormalProblemTagSerializer
    permission_classes = [permissions.AllowAny]


class ProblemTagRetrieveView(generics.RetrieveAPIView):
    queryset = ProblemTag.objects.all()
    serializer_class = NormalProblemTagSerializer
    permission_classes = [permissions.AllowAny]
