from zipfile import ZipFile

from rest_framework import serializers

from problem.models import Problem, ProblemTag, TestCase
from utils.tools import get_languages


# 基本序列化器
class ListProblemInProblemTag(serializers.RelatedField):
    def to_internal_value(self, data):
        return super().to_internal_value(data)

    def to_representation(self, value):
        return {"id": value.id, "title": value.title}


class BaseProblemTagSerializer(serializers.ModelSerializer):
    problems = ListProblemInProblemTag(many=True, read_only=True)

    class Meta:
        model = ProblemTag
        fields = '__all__'


class BaseProblemSerializer(serializers.ModelSerializer):
    tags = serializers.StringRelatedField(many=True)

    def to_internal_value(self, data):
        if tags_id := data.get('tags'):
            for tag_id in tags_id:
                try:
                    ProblemTag.objects.get(id=tag_id)
                except ProblemTag.DoesNotExist:
                    raise serializers.ValidationError({"detail": f"tag id '{tag_id}' does not exists"})
            tags = ProblemTag.objects.filter(id__in=tags_id)
            data.update(tags=tags)
        return data

    def validate(self, data):
        for i in data.get('languages'):
            if i not in get_languages().keys():
                raise serializers.ValidationError({"detail": "specify language does not support"})
        if tc_id := data.get('test_case'):
            try:
                test_case = TestCase.objects.get(id=tc_id)
            except TestCase.DoesNotExist:
                raise serializers.ValidationError({"detail": "this test case does not exist"})
            data.update(test_case=test_case)
        elif self.instance:
            test_case = self.instance.test_case
        else:
            raise serializers.ValidationError({"detail": "test case cannot be null"})

        if self.instance and data.get('point') is None:
            return data

        tc_struct = test_case.struct
        if point := data.get('point'):
            if len(tc_struct) != len(point):
                raise serializers.ValidationError("point invalid")
            for ori, cmp in zip(tc_struct, point):
                if not (cmp.__contains__('input_name') and cmp.__contains__('output_name')):
                    raise serializers.ValidationError({"detail": "point invalid"})
                if data.get('mode') == 'OI' and (not cmp.__contains__('point')):
                    raise serializers.ValidationError({"detail": "point invalid"})
                if ori.get('input_name') != cmp.get('input_name'):
                    raise serializers.ValidationError({"detail": "point invalid"})
                if ori.get('output_name') != cmp.get('output_name'):
                    raise serializers.ValidationError({"detail": "point invalid"})
        else:
            raise serializers.ValidationError({"detail": "point is null"})
        return data

    class Meta:
        model = Problem
        fields = '__all__'
        read_only_fields = ['created_time', 'last_update_time', 'statistics']


class BaseTestCaseSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        with ZipFile(attrs.get('file')) as f:
            namelist = f.namelist()
            in_list = [i.split('.')[0] for i in namelist if i.endswith('in')]
            out_list = [i.split('.')[0] for i in namelist if i.endswith('out')]
            back_in = in_list.copy()
            back_out = out_list.copy()
            if len(in_list) == 0 or len(out_list) == 0 or len(in_list) != len(out_list):
                raise serializers.ValidationError(
                    {"detail": "the test case is empty or number of input and output not match"}
                )
            while len(in_list) != 0:
                try:
                    out_list.remove(in_list.pop())
                except ValueError:
                    serializers.ValidationError({"detail": "number of input and output not match"})
            if len(out_list) != 0:
                serializers.ValidationError({"detail": "number of input and output not match"})
            struct = list()
            for bi, bo in zip(back_in, back_out):
                struct.append(
                    {
                        "input_name": bi + ".in",
                        "output_name": bo + ".out"
                    }
                )
            attrs.update(struct=struct)
        return attrs

    class Meta:
        model = TestCase
        fields = '__all__'


# 问题标签序列化器
class AdminProblemTagSerializer(BaseProblemTagSerializer):
    class Meta:
        model = ProblemTag
        fields = '__all__'


class NormalProblemTagSerializer(BaseProblemTagSerializer):
    class Meta:
        model = ProblemTag
        fields = '__all__'
        read_only_fields = ['tag_name']


# 问题序列化器
class AdminProblemSerializer(BaseProblemSerializer):
    class Meta:
        model = Problem
        fields = '__all__'


class NormalProblemSerializer(BaseProblemSerializer):
    class Meta:
        model = Problem
        fields = [
            'id', 'title', 'desc', 'input_desc', 'output_desc', 'sample', 'hint', 'languages', 'time_limit', 'point',
            'memory_limit', 'difficulty', 'difficulty', 'tags', 'source', 'statistics'
        ]
        read_only_fields = [
            'id', 'title', 'desc', 'input_desc', 'output_desc', 'sample', 'hint', 'languages', 'time_limit', 'point',
            'memory_limit', 'difficulty', 'difficulty', 'tags', 'source', 'statistics'
        ]


class ProblemListSerializer(BaseProblemSerializer):
    class Meta:
        model = Problem
        fields = ['id', 'title', 'difficulty', 'tags', 'statistics']


class SpecialProblemListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Problem
        fields = ['id', 'title']


class GeneralTestCaseSerializer(BaseTestCaseSerializer):
    class Meta:
        model = TestCase
        fields = '__all__'
        read_only_fields = ['created_time', 'struct']
