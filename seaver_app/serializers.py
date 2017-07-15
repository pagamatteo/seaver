# -*- coding: utf-8 -*-
"""
Contiene gli oggetti serializzati: tradotti da python a json, etc...
"""
from .models import File as FileModel, Workspace, BulkWriter, FileData, PunctualAnnotationEvent, \
    IntervalAnnotationEvent, FileFieldName, PunctualAnnotation, IntervalAnnotation
from rest_framework import serializers
from .csvreader import CSVReader, FileToStrings, StringsToLines, NumberOfFieldsChangedException
from django.contrib.auth.models import User
from django.urls import reverse
import urllib.parse


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        read_only_fields =("id", "last_login", "is_superuser", "is_staff", "is_active", "date_joined", "groups",
                           "user_permissions")
        exclude = ('password', )


class WorkspaceSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Workspace
        fields = ('url', 'user', 'name', 'modified_on', 'files', 'punctual_annotations', 'interval_annotations')


class FileSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = FileModel
        fields = ('url', 'workspace', 'name', 'active', 'offset', 'stretching', 'field_names')
        read_only_fields = ('workspace', )


class FileFieldSerializer(serializers.HyperlinkedModelSerializer):
    # url to get field data
    field_data = serializers.SerializerMethodField()

    class Meta:
        model = FileFieldName
        fields = ('url', 'file', 'name', 'computed', 'active', 'field_data')

    def get_field_data(self, obj):
        p = reverse('fielddata-detail', args=[obj.pk])
        field_data_url = self.context['request'].build_absolute_uri(p)

        return field_data_url


class PunctualAnnotationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PunctualAnnotation
        fields = ('url', 'pk', 'name', 'description')


class PunctualAnnotationEventSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = PunctualAnnotationEvent
        fields = ('url', 'pk', 'annotation', 'workspace', 'start')


class IntervalAnnotationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = IntervalAnnotation
        fields = ('url', 'pk', 'name', 'description')


class IntervalAnnotationEventSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = IntervalAnnotationEvent
        fields = ('url', 'pk', 'annotation', 'workspace', 'start', 'stop')


class FileUploadSerializer(serializers.Serializer):
    """
    Serializzazione di un file in upload
    """
    # workspace al quale si riferisce
    workspace = serializers.PrimaryKeyRelatedField(queryset=Workspace.objects.all())
    file_data = serializers.FileField()

    class Meta:
        fields = ('workspace', 'file_data')

    def create(self, validated_data):
        """
        Crea i modelli a partire dall'oggetto serializzato
        :param validated_data:
        :return:
        """
        # creo il modello del file
        file_model = FileModel()
        workspace = Workspace.objects.get(pk=validated_data.get('workspace'))
        file_model.workspace = workspace
        file_uploaded = validated_data.get('file_data')
        # ottengo un nome valido per il file (non già usato)
        file_model.name = FileModel.get_valid_name(workspace, file_uploaded.name)
        file_model.save()

        # creo il lettore csv
        csv_reader = CSVReader(StringsToLines(FileToStrings(file_uploaded)))
        # creo il db bulk writer
        bulk_writer = BulkWriter(FileData)

        try:
            # leggo numero riga, numero colonna, valore
            for r, c, value in csv_reader:
                # costruisco il file data
                file_data = FileData()
                file_data.file = file_model
                file_data.field_index = r
                file_data.field_name = 'field{}'.format(c)
                file_data.field_value = value

                bulk_writer.append(file_data)

            bulk_writer.flush()
        except Exception as e:
            # se c'è stato un errore cancello il file
            file_model.delete()
            raise e


class FieldDataSerializer(serializers.Serializer):
    """
    Data di field
    """
    field_data = serializers.ListField(serializers.FloatField())


class FieldAnalysisFftOptionsSerializer(serializers.Serializer):
    """
    Campi opzionali per l'analisi FFT
    """
    n = serializers.IntegerField(required=False)
    norm = serializers.ChoiceField(
        ('ortho', None),
        required=False
    )


class FieldAnalysisEwmaOptionsSerializer(serializers.Serializer):
    """
    Campi opzionali per l'analisi EWMA
    """
    com = serializers.FloatField(required=False)
    span = serializers.FloatField(required=False)
    halflife = serializers.FloatField(required=False)
    min_periods = serializers.IntegerField(required=False)
    freq = serializers.CharField(max_length=20, required=False)
    adjust = serializers.BooleanField(required=False)
    how = serializers.CharField(max_length=20, required=False)

    def validate(self, attrs):
        if ('com' not in attrs) and ('span' not in attrs) and ('halflife' not in attrs):
            raise serializers.ValidationError('you must provide one of these: com, span or halflife')

        return attrs


class FieldAnalysisOptionsSerializer(serializers.Serializer):
    """
    opzioni per l'analisi
    """
    fft = FieldAnalysisFftOptionsSerializer(required=False)
    ewma = FieldAnalysisEwmaOptionsSerializer(required=False)


class FieldAnalysisRequestSerializer(serializers.Serializer):
    """
    Usata per richiedere la creazione di un'analisi
    """
    name = serializers.CharField(max_length=20)

    type = serializers.ChoiceField(
        (
            ('fft', 'Fast Fourier Transform'),
            ('ewma', 'Exponentially-weighted moving average')
        )
    )

    options = FieldAnalysisOptionsSerializer(required=False)

    def validate(self, attrs):
        if (attrs['type'] == 'ewma') and ('options' not in attrs):
            serializers.ValidationError('with ewma you must provide options field')
