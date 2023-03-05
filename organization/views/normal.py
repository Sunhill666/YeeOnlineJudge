from django.contrib.auth.hashers import check_password
from rest_framework import generics
from rest_framework import status, permissions, filters
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from organization.models import User, Group
from organization.serializers import RegisterSerializer, NormalUserSerializer, UserRankListSerializer, GroupsSerializer
from utils.pagination import NumPagination


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GroupRetrieveView(generics.RetrieveAPIView):
    queryset = Group.objects.all()
    serializer_class = GroupsSerializer
    permission_classes = [permissions.AllowAny]


class UserRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = NormalUserSerializer

    def get_queryset(self):
        if self.request.method == "GET":
            return User.objects.all()
        return User.objects.filter(username=self.request.user.username)

    def update(self, request, *args, **kwargs):
        if request.data.get('password', None):
            if old_pwd := request.data.get('old_pwd', None):
                instance = self.get_object()
                if not check_password(old_pwd, instance.password):
                    return Response({"detail": "旧密码错误"}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({"detail": "未携带旧密码"}, status=status.HTTP_400_BAD_REQUEST)
        return super().update(request, *args, **kwargs)


class UserRankList(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    serializer_class = UserRankListSerializer
    pagination_class = NumPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["=username", "profile__group__name"]
    ordering_fields = ["accepted_num", "commit_num"]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(
            User.objects.all().order_by(
                "-profile__statistics__Accepted",
                "profile__statistics__Commit",
                "username"
            )
        )
        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = self.get_serializer(instance=page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
