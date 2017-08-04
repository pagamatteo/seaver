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
    # url used to get field data
    field_data = serializers.SerializerMethodField()
    # url used to create filed analysis
    analysis_url = serializers.SerializerMethodField()

    class Meta:
        model = FileFieldName
        fields = ('url', 'file', 'name', 'computed', 'active', 'field_data', 'analysis_url')

    def get_field_data(self, obj):
        p = reverse('fielddata-detail', args=[obj.pk])
        field_data_url = self.context['request'].build_absolute_uri(p)

        return field_data_url

    def get_analysis_url(self, obj):
        p = reverse('analysis-detail', args=[obj.pk])
        analysis_url = self.context['request'].build_absolute_uri(p)

        return analysis_url


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
        required=False,
        allow_null=True
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
            raise serializers.ValidationError('with ewma you must provide options field')

        return attrs
