from rest_framework import viewsets
from organization.models import User, Classes
from organization.serializers import UserSerializer, ClassesSerialize


class UserViewSet(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.all()


class ClassViewSet(viewsets.ModelViewSet):
    serializer_class = ClassesSerialize
    queryset = Classes.objects.all()
