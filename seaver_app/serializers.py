from .models import File as FileModel, Workspace
from rest_framework import routers, serializers, viewsets


class WorkSpaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workspace
        fields = {}

class FileSerializer(serializers.ModelSerializer):
    # workspace_name = serializers.CharField(max_length=50)

    class Meta:
        model = FileModel
        fields = ('name', 'active', 'offset', 'stretching')