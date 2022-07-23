from rest_framework import serializers

from problems.models import Problem, ProblemTag


class ProblemTagSerializers(serializers.ModelSerializer):
    problems = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = ProblemTag
        fields = "__all__"


class ProblemSerializers(serializers.ModelSerializer):
    difficulty = serializers.ChoiceField(choices=Problem.Difficulty.choices)
    languages = serializers.ListField(child=serializers.ChoiceField(choices=Problem.OJLanguage.choices))
    tags = serializers.SlugRelatedField(many=True, slug_field='tag_name', queryset=ProblemTag.objects.all())

    class Meta:
        model = Problem
        fields = "__all__"
        read_only = ['commit_num', 'accept_num', 'statistics_info', 'create_by']
