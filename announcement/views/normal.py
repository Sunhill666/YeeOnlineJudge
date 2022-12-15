from rest_framework import generics, filters, permissions

from utils.pagination import NumPagination
from ..models import Announcement
from ..serializers import AnnouncementListSerializer, NormalAnnouncementDetailSerializer


class AnnouncementListView(generics.ListAPIView):
    queryset = Announcement.objects.filter(contest__isnull=True)
    serializer_class = AnnouncementListSerializer
    pagination_class = NumPagination
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['created_time']
    search_fields = ['title', 'content']


class AnnouncementRetrieveView(generics.RetrieveAPIView):
    queryset = Announcement.objects.filter(contest__isnull=True)
    serializer_class = NormalAnnouncementDetailSerializer
    permission_classes = [permissions.AllowAny]
