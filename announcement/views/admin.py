from rest_framework import filters
from rest_framework import generics

from announcement.models import Announcement
from announcement.serializers import AnnouncementListSerializer, AnnouncementSerializer
from organization import permissions
from utils.pagination import NumPagination


class AnnouncementListCreateView(generics.ListCreateAPIView):
    queryset = Announcement.objects.all().order_by('id')
    pagination_class = NumPagination
    permission_classes = [permissions.IsStaff]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['created_time']
    search_fields = ['title', 'content']

    def get_serializer_class(self):
        if self.request.method == "GET":
            return AnnouncementListSerializer
        return AnnouncementSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class AnnouncementRUDView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Announcement.objects.all()
    serializer_class = AnnouncementSerializer
    permission_classes = [permissions.IsStaff]
