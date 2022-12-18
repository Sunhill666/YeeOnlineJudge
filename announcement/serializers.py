from rest_framework import serializers

from .models import Announcement


class AnnouncementSerializer(serializers.ModelSerializer):
    create_by = serializers.StringRelatedField()

    class Meta:
        model = Announcement
        fields = "__all__"
        read_only_fields = ['created_time', 'last_update_time', 'created_by']


class NormalAnnouncementDetailSerializer(AnnouncementSerializer):
    class Meta:
        model = Announcement
        exclude = ['visible']
        read_only_fields = ['title', 'content', 'created_time', 'last_update_time', 'created_by']


class AnnouncementListSerializer(AnnouncementSerializer):
    class Meta:
        model = Announcement
        exclude = ['visible']
