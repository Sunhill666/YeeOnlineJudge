from rest_framework import generics, filters, viewsets

from organization import permissions
from training.models import Training, ProblemSet, LearningPlan
from training.serializers import TrainingListSerializer, BaseTrainingSerializer, \
    BaseProblemSetSerializer, BaseLearningPlanSerializer
from utils.pagination import NumPagination


class ProblemSetViewSet(viewsets.ModelViewSet):
    queryset = ProblemSet.objects.all()
    pagination_class = NumPagination
    permission_classes = [permissions.IsStaff]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title']
    serializer_class = BaseProblemSetSerializer


class TrainingListCreateView(generics.ListCreateAPIView):
    queryset = Training.objects.all().order_by('-start_time')
    pagination_class = NumPagination
    permission_classes = [permissions.IsStaff]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['created_time', 'start_time']

    def get_serializer_class(self):
        if self.request.method == "GET":
            return TrainingListSerializer
        return BaseTrainingSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class TrainingRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Training.objects.all()
    serializer_class = BaseTrainingSerializer
    permission_classes = [permissions.IsStaff]


class LearningPlanListCreateView(generics.ListCreateAPIView):
    queryset = LearningPlan.objects.all()
    serializer_class = BaseLearningPlanSerializer
    pagination_class = NumPagination
    permission_classes = [permissions.IsStaff]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title']
    ordering_fields = ['created_time']


class LearningPlanRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = LearningPlan.objects.all()
    serializer_class = BaseLearningPlanSerializer
    permission_classes = [permissions.IsStaff]
