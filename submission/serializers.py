from datetime import datetime

from django.core.cache import cache
from rest_framework import serializers

from problem.models import Problem
from submission.models import Submission


class BaseSubmissionSerializers(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField()

    def validate(self, attrs):
        problem = attrs.get("problem")

        if attrs.get('language_id') not in problem.languages:
            raise serializers.ValidationError({"detail": "language does not support"})

        if training := attrs.get('training'):
            training_verify_set = cache.get('training_verify', set())
            if self.context.get('request').user.username not in training_verify_set:
                raise serializers.ValidationError({"detail": "you do not have permission to access this training"})
            if datetime.now() > training.end_time:
                raise serializers.ValidationError({"detail": "training has expired"})
            if datetime.now() < training.start_time:
                raise serializers.ValidationError({"detail": "training has not started"})

            try:
                training.problems.get(problem=problem)
            except Problem.DoesNotExist:
                raise serializers.ValidationError({"detail": "problem not in this training"})

        return attrs

    def to_internal_value(self, data):
        if data.get('status'):
            status = Submission.translate_status(data.get('status'))
            data.update(status=status)
        return super().to_internal_value(data)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        problem = Problem.objects.get(pk=ret.get('problem'))
        prob_dict = {
            'id': ret.get('problem'),
            'title': problem.title
        }
        ret.update({'problem': prob_dict})
        ret.update({'status': ret.get('status')})
        return ret

    class Meta:
        model = Submission
        fields = '__all__'
        read_only_fields = ['status', 'created_time', 'created_by']


class SubmissionListSerializers(BaseSubmissionSerializers):
    class Meta:
        model = Submission
        exclude = ['token', 'code']
