from rest_framework import status, permissions, serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import File as FileModel, Workspace
from .serializers import FileSerializer
from django.contrib.auth.models import User
from rest_framework.views import APIView
from . import permissions as app_permissions


@api_view(['POST'])
@permission_classes((permissions.AllowAny, ))
def update_file(request):
    user = User.objects.first()

    serializer = FileSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        workspace = Workspace.objects.get(user=user, name=serializer.validated_data['workspace_name'])
        serializer.workspace = workspace
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@permission_classes((app_permissions.IsOwner, ))
class FileView(APIView):

    def get(self, request):
        workspaces = Workspace.objects.filter(user=request.user).all()
        file_models = FileModel.objects.filter(workspace__in=workspaces).all()
        serializer = FileSerializer(file_models, many=True)
        return Response(serializer.data)


    # todo check Filtering against the current user http://www.django-rest-framework.org/api-guide/filtering/
    def post(self, request, format=None):
        user = User.objects.first()

        serializer = FileSerializer(data=request.data)
        if serializer.is_valid():
            workspace = Workspace.objects.get(pk=serializer.validated_data['workspace'])
            if workspace.user != user:
                raise serializers.ValidationError('workspace do not belong to user')
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
