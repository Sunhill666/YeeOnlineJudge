from datetime import datetime

from rest_framework import serializers

from problem.models import Problem
from submission.models import Submission
from training.models import Training
from utils.judger.languages import languages, prob_status


class BaseSubmissionSerializers(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField()

    def validate(self, attrs):
        if attrs.get('language_id') not in languages.keys():
            raise serializers.ValidationError({"detail": "language does not support"})

        try:
            problem = Problem.objects.get(pk=attrs.get("problem"))
        except Problem.DoesNotExist:
            raise serializers.ValidationError({"detail": "problem does not exist"})

        if training_id := attrs.get('training'):
            try:
                training = Training.objects.get(pk=training_id)
            except Training.DoesNotExist:
                return serializers.ValidationError({"detail": "training does not exist"})

            if datetime.now() > training.end_time:
                return serializers.ValidationError({"detail": "training has expired"})
            if datetime.now() < training.start_time:
                return serializers.ValidationError({"detail": "training has not started"})

            try:
                training.problems.get(problem=problem)
            except Problem.DoesNotExist:
                return serializers.ValidationError({"detail": "problem not in this training"})

        return attrs

    def to_internal_value(self, data):
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
        ret.update({'status': prob_status.get(ret.get('status'))})
        return ret

    class Meta:
        model = Submission
        fields = '__all__'
        read_only_fields = ['status', 'created_time', 'created_by']
