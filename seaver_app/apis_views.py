# -*- coding: utf-8 -*-
"""
Le view degli oggetti serializzati
"""
from rest_framework import status, permissions, serializers, generics, routers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import File as FileModel, Workspace
from .serializers import FileSerializer, FileUploadSerializer, UserSerializer
from django.contrib.auth.models import User
from rest_framework.views import APIView
from . import permissions as app_permissions
from django.http import Http404


# @api_view(['POST'])
# @permission_classes((permissions.AllowAny, ))
# def update_file(request):
#     user = User.objects.first()
#
#     serializer = FileSerializer(data=request.data)
#     if serializer.is_valid(raise_exception=True):
#         workspace = Workspace.objects.get(user=user, name=serializer.validated_data['workspace_name'])
#         serializer.workspace = workspace
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @permission_classes((app_permissions.IsOwner, ))
# class FileView(APIView):
#
#     def get(self, request):
#         workspaces = Workspace.objects.filter(user=request.user).all()
#         file_models = FileModel.objects.filter(workspace__in=workspaces).all()
#         serializer = FileSerializer(file_models, many=True)
#         return Response(serializer.data)
#
#
#     # todo check Filtering against the current user http://www.django-rest-framework.org/api-guide/filtering/
#     def post(self, request, format=None):
#         user = User.objects.first()
#
#         serializer = FileSerializer(data=request.data)
#         if serializer.is_valid():
#             workspace = Workspace.objects.get(pk=serializer.validated_data['workspace'])
#             if workspace.user != user:
#                 raise serializers.ValidationError('workspace do not belong to user')
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def perform_create(self, serializer):
#         serializer.save(owner=self.request.user)

@permission_classes((permissions.IsAuthenticated, ))
class UserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_queryset(self):
        # solo l'utente corrente può accedere ai propri dati
        return User.objects.filter(pk=self.request.user.pk)


@permission_classes((permissions.IsAuthenticated, ))
class FileListView(generics.ListAPIView):
    serializer_class = FileSerializer

    def get_queryset(self):
        user = self.request.user
        workspaces = Workspace.objects.filter(user=user)
        return FileModel.objects.filter(workspace__in=workspaces)


@permission_classes((permissions.IsAuthenticated, ))
class FileDetailedView(generics.RetrieveUpdateAPIView, generics.ListAPIView):
    serializer_class = FileSerializer

    def get_queryset(self):
        user = self.request.user
        workspaces = Workspace.objects.filter(user=user)
        return FileModel.objects.filter(workspace__in=workspaces)


# todo non testata
@permission_classes((permissions.IsAuthenticated, ))
class FileUploadedView(APIView):

    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            try:
                workspace = Workspace.objects.get(serializer.validated_data.get('workspace'))
            except Workspace.DoesNotExist:
                raise Http404('Workspace not found')
            workspaces = Workspace.objects.filter(user=user)
            if workspace not in workspaces:
                # return Response('Workspace not found')
                raise Http404('Workspace not found')

            # salva i modelli a partire dall'oggetto serializzato
            serializers.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# router = routers.DefaultRouter()
# # router.register(r'user', UserView, 'user')
# router.register(r'file', FileListView, 'file-list')
# # router.register(r'file/(?P<pk>[0-9]+)', FileDetailedView, 'file-detailed')
# router.register(r'file-upload', FileUploadedView, 'file-upload')

