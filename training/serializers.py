from django.contrib.auth.hashers import make_password
from django.core.cache import cache
from django.db.models import Q
from rest_framework import serializers

from announcement.models import Announcement
from announcement.serializers import NormalAnnouncementDetailSerializer
from organization.models import Group, User
from organization.serializers import GroupAllSerializer, UserAllSerializer
from problem.serializers import ProblemListSerializer
from training.models import Training, TrainingRank, ProblemSet, LearningPlan


# 基本序列化器
class BaseProblemSetSerializer(serializers.ModelSerializer):
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        serializer = ProblemListSerializer(instance=instance.problems, many=True, context=self.context)
        ret.update(problems=serializer.data)
        return ret

    class Meta:
        model = ProblemSet
        fields = '__all__'


class BaseTrainingSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, write_only=True, required=False)
    group = GroupAllSerializer(many=True, required=False)
    user = UserAllSerializer(many=True, required=False)
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

        data.update(mode="ACM")

        problem_id = []
        point = []
        if problems := data.get('problems'):
            for problem in problems:
                problem_id.append(problem.get('id'))
                point.append(problem)
            data.update(problems=problem_id)
            data.update(point=point)

        return data

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        self.context.update(training=instance.id)
        serializer = ProblemListSerializer(instance=instance.problems, many=True, context=self.context)
        ann = NormalAnnouncementDetailSerializer(
            instance=Announcement.objects.filter(
                Q(visible=True) & Q(training=instance.id)
            ).order_by('-created_time'),
            many=True
        )
        problems = []
        points = ret.get('point')
        for problem in serializer.data:
            for point in points:
                if point.get('id') == problem.get('id'):
                    problem.update(point=point.get('point'))
                    break
            problems.append(problem)
        ret.pop('point')
        ret.update(problems=problems)
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
        if attrs.get('start_time'):
            if attrs['start_time'] > attrs['end_time']:
                raise serializers.ValidationError({"detail": "end time should be later than start time"})
        return attrs

    class Meta:
        model = Training
        exclude = ['mode', 'is_open']
        read_only_fields = ['created_time', 'created_by']


class BaseLearningPlanSerializer(serializers.ModelSerializer):
    create_by = serializers.StringRelatedField()

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        serializer = BaseProblemSetSerializer(instance=instance.stage, many=True, context=self.context)
        ret.update(stage=serializer.data)
        return ret

    def validate(self, attrs):
        if attrs.get('stage') and attrs.get('ordering'):
            stage = attrs['stage']
            order = attrs['ordering']
            if len(stage) != len(order):
                raise serializers.ValidationError({"detail": "stage and ordering must match"})
            for i in stage:
                try:
                    order.index(i.id)
                except ValueError:
                    raise serializers.ValidationError({"detail": "stage and ordering must match"})
        return attrs

    class Meta:
        model = LearningPlan
        fields = '__all__'
        read_only_fields = ['created_time', 'created_by']


class BaseContestRankSerializer(serializers.ModelSerializer):
    group = serializers.StringRelatedField()
    user = serializers.StringRelatedField()

    class Meta:
        model = TrainingRank
        fields = '__all__'
        read_only_fields = ['statistics']


# 训练序列化器
class NormalDetailTrainingSerializer(BaseTrainingSerializer):
    def to_representation(self, instance):
        pk = self.context.get('training')
        self.context.update({"training": pk})
        return super().to_representation(instance)

    class Meta:
        model = Training
        fields = '__all__'


class TrainingListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Training
        exclude = ['description', 'password', 'point', 'problems', 'mode']


class NormalDetailLearningPlanSerializer(BaseLearningPlanSerializer):
    class Meta:
        model = LearningPlan
        fields = '__all__'
