from rest_framework import generics

from organization.models import User, Classes
from organization.serializers import UserSerializer, ClassesSerialize


class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ClassList(generics.ListCreateAPIView):
    queryset = Classes.objects.all()
    serializer_class = ClassesSerialize


class ClassDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Classes.objects.all()
    serializer_class = ClassesSerialize
