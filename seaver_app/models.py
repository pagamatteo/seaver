# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class BulkWriter:
    """
    Scrive sul db ogni batch_size records
    """
    def __init__(self, model, batch_size=500):
        self.model = model
        self.batchSize = batch_size
        self.entries = []

    def flush(self):
        """
        Forza la scrittura su db
        :return:
        """
        self.model.objects.bulk_create(self.entries)
        self.entries.clear()

    def append(self, entry):
        """
        Aggiunge un entry ed eventualmente scrive su db
        :param entry:
        :return:
        """
        self.entries.append(entry)

        if len(self.entries) >= self.batchSize:
            self.flush()


class Workspace(models.Model):
    """
    Classe che modella un workspace.
    """
    user = models.ForeignKey(
        User,
        related_name='workspaces'
    )

    name = models.CharField(max_length=50)
    modified_on = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'name')
        index_together = [['user', 'name']]

    def __str__(self):
        return '{}, {}'.format(self.name, self.user.username)

    def clean(self):
        """
        Definisce la validazione custom del modello
        :return:
        """
        # controlla che il nome non sia vuoto a seguito di rstrip
        self.name = self.name.rstrip()
        if len(self.name) == 0:
            raise ValidationError({'name': '{} is not a valid name'.format(self.name)})

    @classmethod
    def get_or_set(cls, user, name, do_save=True):
        """
        Ottiene o crea il modello se non esiste
        :param user:
        :param name:
        :param do_save: se True, salva il modello nel db
        :return:
        """
        try:
            w = cls.objects.get(user=user, name=name)
        except cls.DoesNotExist:
            w = cls()
            w.user = user
            w.name = name
            if do_save:
                w.save()

        return w

    @classmethod
    def all_ordered_by_date(cls, user):
        """
        Restituisce tutti gli elementi ordinati per data di modifica descrescente
        :param user:
        :return:
        """
        return cls.objects.filter(user=user).order_by('-modified_on')


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
    stretching = models.FloatField(default=1)

    class Meta:
        unique_together = ('workspace', 'name')
        index_together = [['workspace', 'name']]

    def clean(self):
        """
        Definisce la validazione custom del modello
        :return:
        """
        if self.stretching <= 0:
            raise ValidationError({'streatching': 'value {} is not > 0'.format(self.stretching)})

    def __str__(self):
        return str(self.name)

    @classmethod
    def get_valid_name(cls, workspace, name, index=-1):
        """
        Restituisce un nome di file disponibile
        :param name:
        :param index:
        :return:
        """
        if index == -1:
            name_to_check = name
        else:
            name_to_check = '{} ({})'.format(name, index)
        if cls.objects.filter(workspace=workspace, name=name_to_check).exists():
            return cls.get_valid_name(workspace, name, index + 1)

        return name_to_check


class FileFieldName(models.Model):
    """
    Classe che modella i nomi dei campi del file
    """
    file = models.ForeignKey(
        File,
        related_name='field_names',
        on_delete=models.CASCADE
    )
    name = models.CharField(max_length=20)
    # if the field is computer using other fields
    computed = models.BooleanField(default=False)
    # if the is visible in the chart
    active = models.BooleanField(default=False)

    class Meta:
        unique_together = ('file', 'name')

    def __str__(self):
        return '{}, {}'.format(self.file.name, self.name)


class FileData(models.Model):
    """
    Classe che modella i dati contenuti all'interno di un file presente in un certo workspace.
    """
    field_name = models.ForeignKey(
        FileFieldName,
        related_name='field_datas',
        on_delete=models.CASCADE
    )
    field_index = models.PositiveIntegerField()
    field_value = models.FloatField()

    class Meta:
        unique_together = ('field_name', 'field_index')
        index_together = [['field_name', 'field_index']]

    def __str__(self):
        return '{}, {}, {}'.format(self.field_name, self.field_index,
                                       self.field_value)

    @classmethod
    def get_all_data(cls, field):
        query = cls.objects.filter(field_name=field).order_by('field_index')

        data = []
        for file_data in query:
            data.append(file_data.field_value)

        return data

class PunctualAnnotation(models.Model):
    """
    Classe che modella un'annotazione puntuale.
    """
    name = models.CharField(max_length=20, unique=True)#, primary_key=True)
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
    workspace = models.ForeignKey(
        Workspace,
        related_name= 'punctual_annotations',
        on_delete=models.CASCADE
    )
    # index = models.PositiveIntegerField()
    offset = models.FloatField(default=0)

    # class Meta:
    #     # unique_together = ('workspace', 'index')
    #     # index_together = [['workspace', 'index']]
    #     index_together = [['workspace']]


class IntervalAnnotation(models.Model):
    """
    Classe che modella un'annotazione con durata.
    """
    name = models.CharField(max_length=20, unique=True)#, primary_key=True)
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
    workspace = models.ForeignKey(
        Workspace,
        related_name='interval_annotations',
        on_delete=models.CASCADE
    )
    # index = models.PositiveIntegerField()
    start = models.FloatField()
    stop = models.FloatField()

    # class Meta:
    #     unique_together = ('workspace', 'index')
    #     index_together = [['workspace', 'index']]
    #     index_together = [['workspace']]

    def clean(self):
        """
        Definisce la validazione custom del modello
        :return:
        """
        if self.stop <= self.start:
            raise ValidationError({'stop': 'stop {} must be > start {}'.format(self.stop, self.start)})
