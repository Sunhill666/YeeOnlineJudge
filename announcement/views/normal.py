from django.db.models import Q
from rest_framework import generics, filters, permissions

from utils.pagination import NumPagination
from announcement.models import Announcement
from announcement.serializers import AnnouncementListSerializer, NormalAnnouncementDetailSerializer


class AnnouncementListView(generics.ListAPIView):
    queryset = Announcement.objects.filter(Q(visible=True) & Q(training__isnull=True))
    serializer_class = AnnouncementListSerializer
    pagination_class = NumPagination
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['created_time']
    search_fields = ['title', 'content']


class AnnouncementRetrieveView(generics.RetrieveAPIView):
    queryset = Announcement.objects.filter(Q(visible=True) & Q(training__isnull=True))
    serializer_class = NormalAnnouncementDetailSerializer
    permission_classes = [permissions.AllowAny]
