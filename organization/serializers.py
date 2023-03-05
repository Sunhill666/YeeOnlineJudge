import re

from rest_framework import serializers

from .models import User, Group, UserProfile


# 基本序列化器
class BaseGroupsSerialize(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = '__all__'


class BaseUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=128, min_length=8, write_only=True, allow_blank=True)

    def create(self, validated_data):
        profile = validated_data.pop('profile')
        user = User.objects.create_user(**validated_data)
        UserProfile.objects.create(user=user, **profile)
        return user

    def update(self, instance, validated_data):
        if pwd := validated_data.pop("password", None):
            instance.set_password(pwd)

        if profile_data := validated_data.pop('profile', None):
            profile = instance.profile
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return super().update(instance, validated_data)

    class Meta:
        model = User
        fields = '__all__'
        read_only_fields = ['date_joined', 'last_login']


class BaseUserProfileSerializer(serializers.ModelSerializer):
    group = BaseGroupsSerialize()

    def to_internal_value(self, data):
        if group_name := data.get('group'):
            try:
                group = Group.objects.get(name=group_name)
            except Group.DoesNotExist:
                raise serializers.ValidationError({"detail": f"'{group_name}' group does not exist"})
            data['group'] = group
        return data

    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ['statistics']


# 组序列化
class ForGroupSerializer(BaseUserProfileSerializer):
    profile = serializers.SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        model = UserProfile
        fields = ['profile', 'user', 'avatar']


class GroupsSerializer(BaseGroupsSerialize):
    users = ForGroupSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = '__all__'


# 用户资料序列化器
class AdminUserProfileSerializer(BaseUserProfileSerializer):
    class Meta:
        model = UserProfile
        exclude = ['id', 'user']


class NormalUserProfileSerializer(BaseUserProfileSerializer):
    class Meta:
        model = UserProfile
        exclude = ['id', 'user']


class GeneralUserProfileListSerializer(BaseUserProfileSerializer):
    class Meta:
        model = UserProfile
        fields = ['group', 'avatar']


class UserProfileRankListSerializer(BaseUserProfileSerializer):
    class Meta:
        model = UserProfile
        fields = ['group', 'avatar', 'statistics']


# 用户序列化器
class AdminUserSerializer(BaseUserSerializer):
    profile = AdminUserProfileSerializer()

    class Meta:
        model = User
        fields = '__all__'


class NormalUserSerializer(BaseUserSerializer):
    profile = NormalUserProfileSerializer()

    class Meta:
        model = User
        fields = ['username', 'nickname', 'real_name', 'email', 'date_joined', 'profile', 'password']
        read_only_fields = ['username']


class GeneralUserListSerializer(BaseUserSerializer):
    profile = GeneralUserProfileListSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['username', 'nickname', 'email', 'user_role', 'is_staff', 'is_superuser', 'profile']


# 注册序列化器
class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=13, min_length=8)
    nickname = serializers.CharField(max_length=25)
    password = serializers.CharField(max_length=128)
    first_name = serializers.CharField(max_length=10)
    last_name = serializers.CharField(max_length=5)
    email = serializers.EmailField()
    group = serializers.CharField(max_length=25)
    avatar = serializers.ImageField(use_url=True, allow_empty_file=True, required=False)
    bio = serializers.CharField(max_length=50, allow_blank=True, allow_null=True, required=False)

    def to_representation(self, instance):
        register_ret = NormalUserSerializer(instance).data
        up_ret = NormalUserProfileSerializer(UserProfile.objects.get(user=instance)).data
        register_ret.update({'profile': up_ret})
        return register_ret

    def validate_group(self, value):
        try:
            Group.objects.get(name=value)
        except Group.DoesNotExist:
            raise serializers.ValidationError({"detail": f"'{value}' group does not exist"})
        return value

    def validate_username(self, value):
        pattern = re.compile(r"^[0-9]{8,13}\Z")
        match = pattern.match(value)
        if not match:
            raise serializers.ValidationError(
                {"detail": f"this username '{value}' is invalid, the username may contain only numbers and length in "
                           f"8-13"}
            )
        return value

    def create(self, validated_data):
        group_name = validated_data.pop('group')
        avatar = validated_data.pop('avatar', None)
        bio = validated_data.pop('bio', None)
        user = User.objects.create_user(**validated_data)
        group = Group.objects.get(name=group_name)
        UserProfile.objects.create(user=user, group=group, avatar=avatar, bio=bio)
        return user

    def update(self, instance, validated_data):
        raise serializers.ValidationError({"detail": "Update operation cannot doing in this serializer"})


class UserRankListSerializer(BaseUserSerializer):
    profile = UserProfileRankListSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['username', 'nickname', 'profile']
