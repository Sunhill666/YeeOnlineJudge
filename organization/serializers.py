from rest_framework.validators import UniqueTogetherValidator

from .models import User, Classes
from rest_framework import serializers


class ClassesSerialize(serializers.ModelSerializer):
    users = serializers.StringRelatedField(many=True, read_only=True)

    class Meta:
        model = Classes
        fields = '__all__'
        read_only_fields = ('id', 'users')


class UserSerializer(serializers.ModelSerializer):
    user_role = serializers.ChoiceField(source="get_user_role_display", choices=User.UserRole.choices)
    user_admin = serializers.ChoiceField(source="get_user_admin_display", choices=User.UserAdmin.choices)
    classes = ClassesSerialize()

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        get_pwd = validated_data.get("password")
        if get_pwd:
            try:
                instance.set_password(get_pwd)
                validated_data.pop("password")
            except:
                pass
        return super().update(instance, validated_data)

    class Meta:
        model = User
        # exclude = ['groups', 'user_admin']
        fields = '__all__'
        read_only_fields = ('id', 'commit_num', 'accept_num', 'solved_num')
