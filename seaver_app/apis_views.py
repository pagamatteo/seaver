# -*- coding: utf-8 -*-
"""
Le view degli oggetti serializzati
"""
from rest_framework import status, permissions, serializers, generics, routers, viewsets, mixins
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from .models import File as FileModel, Workspace, PunctualAnnotationEvent, FileFieldName, FileData, \
    IntervalAnnotation, PunctualAnnotation, IntervalAnnotationEvent
from .serializers import FileSerializer, FileUploadSerializer, UserSerializer, PunctualAnnotationEventSerializer, \
    IntervalAnnotationEventSerializer, WorkspaceSerializer, FileFieldSerializer, FieldDataSerializer, \
    FieldAnalysisRequestSerializer, PunctualAnnotationSerializer, IntervalAnnotationSerializer
from django.contrib.auth.models import User
from rest_framework.views import APIView
from django.http import Http404, HttpResponseServerError
from . import analysis
import logging


logger = logging.getLogger(__name__)


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

# @permission_classes((permissions.IsAuthenticated, ))
# class UserView(generics.RetrieveUpdateAPIView):
#     serializer_class = UserSerializer
#
#     def get_queryset(self):
#         # solo l'utente corrente può accedere ai propri dati
#         return User.objects.filter(pk=self.request.user.pk)
#
#
# @permission_classes((permissions.IsAuthenticated, ))
# class FileListView(generics.ListAPIView):
#     serializer_class = FileSerializer
#
#     def get_queryset(self):
#         user = self.request.user
#         workspaces = Workspace.objects.filter(user=user)
#         return FileModel.objects.filter(workspace__in=workspaces)
#
#
# @permission_classes((permissions.IsAuthenticated, ))
# class FileDetailedView(generics.RetrieveUpdateAPIView, generics.ListAPIView):
#     serializer_class = FileSerializer
#
#     def get_queryset(self):
#         user = self.request.user
#         workspaces = Workspace.objects.filter(user=user)
#         return FileModel.objects.filter(workspace__in=workspaces)


class UserView(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin,
               viewsets.GenericViewSet):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        # solo l'utente corrente può accedere ai propri dati
        return User.objects.filter(pk=self.request.user.pk)
        # return User.objects.all()


@permission_classes((permissions.IsAuthenticated, ))
class WorkspaceView(viewsets.ModelViewSet):
    serializer_class = WorkspaceSerializer

    def get_queryset(self):
        return Workspace.objects.filter(user=self.request.user)


# @permission_classes((permissions.IsAuthenticated, ))
class FileView(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, mixins.DestroyModelMixin,
               viewsets.GenericViewSet):
    serializer_class = FileSerializer
    permission_classes = (permissions.IsAuthenticated, )

    def get_queryset(self):
        user = self.request.user
        workspaces = Workspace.objects.filter(user=user)
        return FileModel.objects.filter(workspace__in=workspaces).order_by('name')

@permission_classes((permissions.IsAuthenticated, ))
class FileFieldView(viewsets.ModelViewSet):
    serializer_class = FileFieldSerializer

    def get_queryset(self):
        user = self.request.user
        workspaces = Workspace.objects.filter(user=user)
        files = FileModel.objects.filter(workspace__in=workspaces)
        return FileFieldName.objects.filter(file__in=files)


@permission_classes((permissions.IsAuthenticated, ))
class PunctualAnnotationView(viewsets.ModelViewSet):
    serializer_class = PunctualAnnotationSerializer
    queryset = PunctualAnnotation.objects.order_by('name')


@permission_classes((permissions.IsAuthenticated, ))
class PunctualAnnotationEventView(viewsets.ModelViewSet):
    serializer_class = PunctualAnnotationEventSerializer

    def get_queryset(self):
        user = self.request.user
        workspaces = Workspace.objects.filter(user=user)
        return PunctualAnnotationEvent.objects.filter(workspace__in=workspaces)


@permission_classes((permissions.IsAuthenticated, ))
class IntervalAnnotationView(viewsets.ModelViewSet):
    serializer_class = IntervalAnnotationSerializer
    queryset = IntervalAnnotation.objects.order_by('name')


@permission_classes((permissions.IsAuthenticated,))
class IntervalAnnotationEventView(viewsets.ModelViewSet):
    serializer_class = IntervalAnnotationEventSerializer

    def get_queryset(self):
        user = self.request.user
        workspaces = Workspace.objects.filter(user=user)
        return IntervalAnnotationEvent.objects.filter(workspace__in=workspaces)

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


@permission_classes((permissions.IsAuthenticated,))
class FieldDataView(APIView):
    """
    View of the data of a field
    """
    def get(self, request, pk):
        """

        :param request:
        :param pk: field pk
        :return:
        """
        user = request.user
        workspaces = Workspace.objects.filter(user=user)
        files = FileModel.objects.filter(workspace__in=workspaces)
        file_field = FileFieldName.objects.filter(file__in=files).filter(pk=pk)

        if not file_field.exists():
            return Http404()

        data = FileData.get_all_data_list(file_field)

        class DataModel:
            def __init__(self, data):
                self.field_data = data

        data_model = DataModel(data)

        serializer = FieldDataSerializer(data_model)

        return Response(serializer.data, status=status.HTTP_200_OK)


@permission_classes((permissions.IsAuthenticated, ))
class AnalysisView(APIView):
    def post(self, request, pk):
        # controllo che l'input sia valido
        serializer = FieldAnalysisRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = request.user
        workspaces = Workspace.objects.filter(user=user)
        files = FileModel.objects.filter(workspace__in=workspaces)
        file_field = FileFieldName.objects.filter(file__in=files).filter(pk=pk)

        if not file_field.exists():
            return Http404()

        file_field = file_field.get()

        # controllo che non esista giù un altro campo con il nome indicato
        analysis_name = serializer.validated_data['name']
        analysis_file = file_field.file
        if FileFieldName.objects.filter(file=analysis_file, name=analysis_name).exists():
            return Response({'name': ['The name {} already exist for file {}'.format(analysis_name, analysis_file)]},
                            status=status.HTTP_400_BAD_REQUEST)

        # creo il nuovo FileFieldName d'analisi
        analysis_field = FileFieldName()
        analysis_field.file = analysis_file
        analysis_field.name = analysis_name
        analysis_field.computed = True
        analysis_field.save()

        # ottengo i dati
        data = FileData.get_all_data_list(file_field)

        analysis_type = serializer.validated_data['type']
        analysis_options = serializer.validated_data.get('options', {})
        try:
            if analysis_type == 'fft':
                # Fast Fourie Transform
                analysis_data = analysis.fft(data, analysis_options.get('fft', {}))
            elif analysis_type == 'ewma':
                analysis_data = analysis.ewma(data, analysis_options.get('ewma', {}))
            else:
                logger.error('{} is not a valid analysis'.format(serializer.validated_data['analysis']))
                return HttpResponseServerError()
        except Exception as e:
            analysis_field.delete()
            logger.warning(e)
            return Response({
                'options': {
                    analysis_type: {
                        'non_field_errors': list(e.args)
                    }
                }
            },
                status=status.HTTP_400_BAD_REQUEST)

        # salvo i nuovi dati
        FileData.save_data(analysis_field, analysis_data)

        # restituisco il nuovo file
        serializer = FileFieldSerializer(analysis_field, context={'request': request})

        return Response(serializer.data, status=status.HTTP_201_CREATED)



router = routers.DefaultRouter()
router.register(r'user', UserView, 'user')
router.register(r'workspace', WorkspaceView, 'workspace')
router.register(r'file', FileView, 'file')
router.register(r'file-field', FileFieldView, 'filefieldname')
router.register(r'punctual', PunctualAnnotationView)
router.register(r'punctual-event', PunctualAnnotationEventView, 'punctualannotationevent')
router.register(r'interval', IntervalAnnotationView)
router.register(r'interval-event', IntervalAnnotationEventView, 'intervalannotationevent')
router.register(r'file-data', FieldDataView, 'filedata')
