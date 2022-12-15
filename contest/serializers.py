from django.contrib.auth.hashers import make_password
from rest_framework import serializers

from announcement.models import Announcement
from announcement.serializers import NormalAnnouncementDetailSerializer
from contest.models import Contest, ContestRank, ProblemSet
from organization.models import Group, User
from problem.serializers import ProblemListSerializer


# 基本序列化器
class BaseProblemSetSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        serializer = ProblemListSerializer(instance=instance.problems, many=True)
        ret.update(problems=serializer.data)
        return ret

    class Meta:
        model = ProblemSet
        fields = '__all__'


class BaseContestSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, write_only=True, required=False)
    group = serializers.StringRelatedField(many=True, required=False)
    user = serializers.StringRelatedField(many=True, required=False)
    create_by = serializers.StringRelatedField()

    def to_internal_value(self, data):
        if groups := data.get('group'):
            for group_id in groups:
                try:
                    Group.objects.get(id=group_id)
                except Group.DoesNotExist:
                    raise serializers.ValidationError({"detail": f"group id '{group_id}' does not exists"})
            data.update(group=Group.objects.filter(id__in=groups))
        else:
            data.update(group=Group.objects.none())

        if users := data.get('user'):
            for user_id in users:
                try:
                    User.objects.get(username=user_id)
                except User.DoesNotExist:
                    raise serializers.ValidationError({"detail": f"username '{user_id}' does not exists"})
            data.update(user=User.objects.filter(username__in=users))
        else:
            data.update(user=User.objects.none())

        return data

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        serializer = BaseProblemSetSerializer(instance=instance.stage, many=True)
        ann = NormalAnnouncementDetailSerializer(instance=Announcement.objects.filter(
            contest=instance.id).order_by('-created_time'), many=True
        )
        ret.update(stage=serializer.data)
        ret.update(announcement=ann.data)
        return ret

    def create(self, validated_data):
        if pwd := validated_data.get('password'):
            validated_data.update({'password': make_password(pwd)})
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if pwd := validated_data.get('password'):
            validated_data.update({'password': make_password(pwd)})
        return super().update(instance, validated_data)

    def validate(self, attrs):
        if attrs['start_time'] > attrs['end_time']:
            raise serializers.ValidationError({"detail": "end time should be later than start time"})
        return attrs

    class Meta:
        model = Contest
        fields = '__all__'
        read_only_fields = ['created_time', 'created_by']


class BaseContestRankSerializer(serializers.ModelSerializer):
    group = serializers.StringRelatedField()
    user = serializers.StringRelatedField()

    class Meta:
        model = ContestRank
        fields = '__all__'
        read_only_fields = ['statistics']


# 竞赛序列化器
class NormalDetailContestSerializer(BaseContestSerializer):
    class Meta:
        model = Contest
        fields = '__all__'


class ContestListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contest
        exclude = ['description', 'ordering', 'password']
