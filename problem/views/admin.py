from rest_framework import viewsets, filters, generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from organization import permissions
from problem.models import Problem, ProblemTag, TestCase
from problem.serializers import ProblemListSerializer, AdminProblemSerializer, GeneralTestCaseSerializer, \
    AdminProblemTagSerializer, SpecialProblemListSerializer
from utils.pagination import NumPagination


class ProblemListCreateView(generics.ListCreateAPIView):
    pagination_class = NumPagination
    permission_classes = [permissions.IsStaff]
    filter_backends = [filters.SearchFilter]
    search_fields = ['=difficulty', 'title', 'tags__tag_name']

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Problem.objects.all()
        return Problem.objects.filter(visible=True)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ProblemListSerializer
        return AdminProblemSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ProblemRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = AdminProblemSerializer
    permission_classes = [permissions.HasPermissionOrReadOnly | permissions.IsSuperAdmin]

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Problem.objects.all()
        return Problem.objects.filter(visible=True)


class ProblemTagViewSet(viewsets.ModelViewSet):
    serializer_class = AdminProblemTagSerializer
    queryset = ProblemTag.objects.all()
    permission_classes = [permissions.IsStaff]
    filter_backends = [filters.SearchFilter]
    search_fields = ['tag_name']


class TestCaseListCreateView(generics.ListCreateAPIView):
    queryset = TestCase.objects.all()
    permission_classes = [permissions.IsStaff]
    pagination_class = NumPagination
    serializer_class = GeneralTestCaseSerializer


class TestCaseDestroyView(generics.DestroyAPIView):
    queryset = TestCase.objects.all()
    permission_classes = [permissions.IsStaff]


@api_view(["get"])
@permission_classes([permissions.IsStaff])
def special_problem_list(request):
    queryset = Problem.objects.filter(visible=True)
    serializer = SpecialProblemListSerializer(queryset, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)
