from rest_framework import generics, filters

from contest.models import Contest, ProblemSet
from contest.serializers import ContestListSerializer, BaseContestSerializer, BaseProblemSetSerializer
from organization import permissions
from utils.pagination import NumPagination


class ProblemSetListCreateView(generics.ListCreateAPIView):
    queryset = ProblemSet.objects.all()
    pagination_class = NumPagination
    permission_classes = [permissions.IsStaff]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']
    serializer_class = BaseProblemSetSerializer


class ProblemSetRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProblemSet.objects.all()
    permission_classes = [permissions.IsStaff]
    serializer_class = BaseProblemSetSerializer


class ContestListCreateView(generics.ListCreateAPIView):
    queryset = Contest.objects.all()
    pagination_class = NumPagination
    permission_classes = [permissions.IsStaff]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['start_time']

    def get_serializer_class(self):
        if self.request.method == "GET":
            return ContestListSerializer
        return BaseContestSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class ContestRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Contest.objects.all()
    serializer_class = BaseContestSerializer
    permission_classes = [permissions.IsStaff]
