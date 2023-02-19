import csv

from django.http import HttpResponse
from rest_framework import generics
from rest_framework import permissions as ps
from rest_framework import viewsets, status, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from organization import permissions
from organization.models import User, Group, UserProfile
from organization.serializers import AdminUserSerializer, GroupsSerializer, GeneralUserListSerializer
from utils.pagination import NumPagination
from utils.tools import get_available_username, get_random_string


class GroupViewSet(viewsets.ModelViewSet):
    serializer_class = GroupsSerializer
    queryset = Group.objects.all()
    pagination_class = NumPagination
    permission_classes = [permissions.IsSuperAdmin]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'users__user__username']


class UserListCreateView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsSuperAdmin]
    pagination_class = NumPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'nickname', 'email', 'user_role', 'is_staff', 'is_superuser']
    ordering_fields = ['username', 'date_joined']

    def get_serializer_class(self):
        if self.request.method == "GET":
            return GeneralUserListSerializer
        return AdminUserSerializer


class UserRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [permissions.IsSuperAdmin]
    serializer_class = AdminUserSerializer


@api_view(["post"])
@permission_classes([ps.AllowAny])
def batch_register(request):
    username_prefix = request.data.get('prefix', "")
    username_suffix = request.data.get('suffix', "")
    user_num = request.data.get('user_num')
    if user_num is None or user_num == 0:
        return Response({"detail": "生成用户数量不能为空或0"}, status=status.HTTP_400_BAD_REQUEST)

    if 13 - 2 - len(username_prefix) - len(username_suffix) < 0:
        return Response({"detail": "前缀与后缀过长"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        username_list = get_available_username(
            prefix=None if len(username_prefix) == 0 else username_prefix,
            suffix=None if len(username_suffix) == 0 else username_suffix,
            length=user_num
        )

    if request.data.get('password'):
        random_pwd = False
    else:
        random_pwd = True

    batch_group = Group.objects.get_or_create(name=request.data.get('group', "批量添加"))

    user_dict = dict()
    for i in username_list:
        password = get_random_string() if random_pwd else request.data.get('password')
        user = User.objects.create_user(username=i, password=password,
                                        real_name="user batch", email="batch@default.com")
        UserProfile.objects.create(user=user, group=batch_group[0])
        user_dict.update({i: password})

    if request.data.get('output_file', False):
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': 'attachment; filename="batch_user.csv"'}
        )
        writer = csv.writer(response)
        writer.writerow(['Username', 'Password'])
        writer.writerows(user_dict.items())
        return response
    else:
        return Response({"detail": user_dict}, status=status.HTTP_201_CREATED)


class MyTokenObtainPairView(TokenObtainPairView):
    def post(self, request, *args, **kwargs):
        resp = super().post(request, *args, **kwargs)
        user = User.objects.get(username=request.data.get('username'))
        if x_forwarded_for := request.META.get('HTTP_X_FORWARDED_FOR'):
            user.last_login_ip = x_forwarded_for.split(',')[0]
        else:
            user.last_login_ip = request.META.get('REMOTE_ADDR')
        user.save()
        return resp
