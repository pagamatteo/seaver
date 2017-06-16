from django.conf.urls import url, include
from django.contrib.auth.models import User
from .models import File as FileModel
from rest_framework import routers, serializers, viewsets


# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email', 'is_staff')


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# class FileSerializer(serializers.HyperlinkedModelSerializer):
#     class Meta:
#         model = FileModel
#         fields = ('name', 'active', 'offset', 'stretching')
#
#
# class FileViewSet(viewsets.ModelViewSet):
#     queryset = FileModel.objects.all()
#     serializer_class = FileSerializer


# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
# router.register(r'file', FileViewSet)

