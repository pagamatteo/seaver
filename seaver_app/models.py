# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User


class Workspace(models.Model):
    """
    Classe che modella un workspace.
    """
    user = models.ForeignKey(
        User,
        related_name='workspaces',
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=50)

    class Meta:
        unique_together = ('user', 'name')


class File(models.Model):
    """
    Classe che modella un file contenuto all'interno di un workspace.
    """
    workspace = models.ForeignKey(
        Workspace,
        related_name='files',
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=50)
    active = models.BooleanField(default=False, db_index=True)
    offset = models.FloatField(default=0)
    stretching = models.FloatField(default=0)

    class Meta:
        unique_together = ('workspace', 'name')


class FileData(models.Model):
    """
    Classe che modella i dati contenuti all'interno di un file presente in un certo workspace.
    """
    file = models.ForeignKey(
        File,
        related_name='file_data',
        on_delete=models.CASCADE
    )
    field_name = models.CharField(max_length=20)
    field_index = models.IntegerField()
    field_value = models.FloatField()

    class Meta:
        unique_together = ('file', 'field_name', 'field_index')


class PunctualAnnotation(models.Model):
    """
    Classe che modella un'annotazione puntuale.
    """
    name = models.CharField(max_length=20)#, primary_key=True)
    description = models.TextField()


class PunctualAnnotationEvent(models.Model):
    """
    Classe che modella un evento associato ad un'annotazione puntuale
    """
    punctual_annotation = models.ForeignKey(
        PunctualAnnotation,
        related_name='events',
        on_delete=models.CASCADE
    )
    index = models.IntegerField()
    offset = models.FloatField(default=0)

    class Meta:
        unique_together = ('punctual_annotation', 'index')


class IntervalAnnotation(models.Model):
    """
    Classe che modella un'annotazione con durata.
    """
    name = models.CharField(max_length=20)#, primary_key=True)
    description = models.TextField()


class IntervalAnnotationEvent(models.Model):
    """
    Classe che modella un evento associato ad un'annotazione con durata.
    """
    interval_annotation = models.ForeignKey(
        IntervalAnnotation,
        related_name='events',
        on_delete=models.CASCADE
    )
    index = models.IntegerField()
    start = models.FloatField()
    stop = models.FloatField()

    class Meta:
        unique_together = ('interval_annotation', 'index')
