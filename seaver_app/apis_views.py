from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import File as FileModel, Workspace
from .serializers import FileSerializer
from django.contrib.auth.models import User
from rest_framework.views import APIView


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


@permission_classes((permissions.AllowAny, ))
class FileView(APIView):

    def get(self, request, format=None):
        file_models = FileModel.objects.all()
        serializer = FileSerializer(file_models, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        user = User.objects.first()

        serializer = FileSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            workspace = Workspace.objects.get(user=user, name=serializer.validated_data['workspace_name'])
            serializer.workspace = workspace
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
