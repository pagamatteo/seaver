# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os import path

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Workspace, File as FileModel, FileData, BulkWriter, FileFieldName
from .forms import *
from django.contrib.auth import login, authenticate
from .csvreader import FileToStrings, StringsToLines, CSVReader, NumberOfFieldsChangedException
from django.core.exceptions import ValidationError
from django.http import JsonResponse, Http404
from django.views.decorators.csrf import ensure_csrf_cookie
from . import workspace_export


@login_required()
def show_workspaces(request):
    """
    Mostra i workspace creati
    :param request:
    :return:
    """
    user = request.user

    q = Workspace.all_ordered_by_date(user)

    workspaces = []
    for e in q:
        workspaces.append((e.name, path.join(request.path, e.name)))

    context = {'workspaces': workspaces, 'username':user.username}
    print(context)

    return render(request, 'seaver_app/workspace_show.html', context)


@login_required()
@ensure_csrf_cookie
def open_workspace(request, name):
    """
    Apre o crea il workspace selezionato
    :param request:
    :param name:
    :return:
    """
    user = request.user

    workspace = Workspace.get_or_set(user, name, do_save=False)

    # valida il modello
    try:
        workspace.full_clean()
    except ValidationError as e:
        # Do something based on the errors contained in e.message_dict.
        # Display them to a user, or handle them programmatically.
        pass

    # cambia la data di ultima modifica
    workspace.save()

    file_upload_form = FileUploadForm()

    files = FileModel.objects.filter(workspace=workspace)



    if request.method == 'POST':
        file_upload_form = FileUploadForm(request.POST, request.FILES)

        if file_upload_form.is_valid():
            # creo il modello del file
            file_model = FileModel()
            file_model.workspace = workspace
            file_uploaded = file_upload_form.cleaned_data['file']
            # ottengo un nome valido per il file (non già usato)
            file_model.name = FileModel.get_valid_name(workspace, file_uploaded.name)
            file_model.save()

            # creo il lettore csv
            csv_reader = CSVReader(StringsToLines(FileToStrings(file_uploaded)))
            # creo il db bulk writer
            bulk_writer = BulkWriter(FileData)

            try:
                # leggo numero riga, numero colonna, valore
                fields_names = {}
                for r, c, value in csv_reader:
                    # se non esiste costruisco il fileFieldName
                    if c not in fields_names:
                        file_field_name = FileFieldName()
                        file_field_name.file = file_model
                        file_field_name.name = 'field{}'.format(c)
                        file_field_name.save()

                        fields_names[c] = file_field_name

                    # costruisco il file data
                    file_data = FileData()
                    file_data.field_index = r
                    file_data.field_name = fields_names[c]
                    file_data.field_value = value

                    bulk_writer.append(file_data)

                bulk_writer.flush()
            except Exception as e:
                # se c'è stato un errore cancello il file
                file_model.delete()
                raise e

    contex = {'wname': workspace.name,
              'form_action': request.path,
              'file_upload_form': file_upload_form,
              'files': files,
              'workspace': workspace    }

    return render(request, 'seaver_app/workspace.html', contex)


@login_required()
def workspace_export_view(request, name):
    user = request.user

    try:
        workspace = Workspace.objects.get(user=user, name=name)
    except Workspace.DoesNotExist as e:
        return Http404()

    # serve solo per vedere se la funzione field_as_series va
    field = FileFieldName.objects.first()
    serie = workspace_export.field_as_series(field)

    return serie

def signup(request):
    """
    Registrazione utente.

    :param request:
    :return:
    """
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            if user is not None:
                login(request, user)
                # Redirect to a success page.
                return redirect('workspaces')
            else:
                # Return an 'invalid login' error message.
                return

    else:
        form = SignUpForm()
    return render(request, 'seaver_app/signup.html', {'form': form})


def create_empty_workspace(request):
    """
    Creazione workspace vuoto.

    :param request:
    :return:
    """

    user = request.user
    form = WorkspaceForm(request.GET)
    if form.is_valid():
        workspace_name = form.cleaned_data.get('workspace_name')
        workspace = Workspace.get_or_set(user, workspace_name, do_save=True)

        # valida il modello
        try:
            workspace.full_clean()
        except ValidationError as e:
            # todo Do something based on the errors contained in e.message_dict.
            # todo Display them to a user, or handle them programmatically.
            pass

        # cambia la data di ultima modifica
        workspace.save()

        response = {'errors': False, 'results': {'workspace_name': workspace_name}}
        return JsonResponse(response)
    else:
        response = {'errors': True, 'results': form.errors}
        return JsonResponse(response)


def delete_workspace(request, workspace_name):
    """
    Eliminazione di un workspace.

    :param request:
    :param name:
    :return:
    """

    response = {'errors': False}
    user = request.user
    # todo controllo parametro ingresso
    workspace = Workspace.get_or_set(user, workspace_name, do_save=False)
    workspace.delete()
    return JsonResponse(response)


def create_file(request):
    """
    Creazione file.

    :param request:
    :return:
    """
    response = {}
    return JsonResponse(response)


def delete_file(request, workspace_name, file_name):
    """
    Eliminazione di un file.

    :param request:
    :param name:
    :return:
    """

    response = {'errors': False}
    print("Ricevuta richiesta di cancellare il file {}/{}".format(workspace_name, file_name))
    user = request.user
    # todo controllo parametro ingresso
    workspace = Workspace.get_or_set(user, workspace_name, do_save=False)
    file = FileModel.objects.get(workspace=workspace, name=file_name)
    file.delete()
    return JsonResponse(response)



