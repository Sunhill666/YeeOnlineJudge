from models import User, Classes
from rest_framework import serializers
from django.conf import settings


class UserSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField(read_only=True)
    # username = serializers.CharField(max_length=10)
    # email = serializers.CharField(max_length=30)
    # first_name = serializers.CharField(max_length=3)
    # last_name = serializers.CharField(max_length=2)
    # user_id = serializers.CharField(max_length=13)
    # is_active = serializers.BooleanField(default=True)
    # user_role = serializers.ChoiceField(choices=User.UserRole, choicesmax_length=2)
    # user_admin = serializers.ChoiceField(choices=User.UserAdmin, choicesmax_length=2)
    # classes = serializers.PrimaryKeyRelatedField()
    # solved_problems = serializers.JSONField(default=dict)
    # avatar = serializers.CharField(default=f"{settings.AVATAR_URI_PREFIX}/default.png")
    #
    # commit_num = serializers.IntegerField(default=0)
    # accept_num = serializers.IntegerField(default=0)
    # solved_num = serializers.IntegerField(default=0)

    class Meta:
        model = User
        fields = '__all__'
