from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import File as FileModel, Workspace
from .serializers import FileSerializer
from django.contrib.auth.models import User


@api_view(['POST'])
def update_file(request):
    user = User.objects.first()

    serializer = FileSerializer(data=request.data)
    if serializer.is_valid():
        workspace = Workspace.objects.get(user=user, name=serializer.workspace_name)
        serializer.workspace = workspace
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)