from rest_framework import serializers

from problem.models import Problem
from submission.models import Submission
from utils.judger import languages
from utils.judger.languages import prob_status


class SubmissionSerializers(serializers.ModelSerializer):
    commit_by = serializers.ReadOnlyField(source="commit_by.username")

    def validate_language_id(self, value):
        if value not in languages.languages.keys():
            raise serializers.ValidationError("该语言不存在")
        return value

    def to_internal_value(self, data):
        status = Submission.translate_status(data.get('status'))
        data['status'] = status
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
        read_only_fields = ['commit_by']
