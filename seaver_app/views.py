# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os import path

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Workspace, File as FileModel, FileData, BulkWriter
from .forms import *
from django.contrib.auth import login, authenticate
from .csvreader import FileToStrings, StringsToLines, CSVReader, NumberOfFieldsChangedException
from django.core.exceptions import ValidationError
from django.http import JsonResponse

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
            for r, c, value in csv_reader:
                # costruisco il file data
                file_data = FileData()
                file_data.file = file_model
                file_data.field_index = r
                file_data.field_name = 'field{}'.format(c)
                file_data.field_value = value

                bulk_writer.append(file_data)

            bulk_writer.flush()
        except NumberOfFieldsChangedException:
            # se c'è stato un errore cancello il file
            file_model.delete()

        # restituisco il modello di file vuoto
        file_upload_form = FileUploadForm()

    contex = {'wname': workspace.name,
              'form_action': request.path,
              'file_upload_form': file_upload_form}

    return render(request, 'seaver_app/workspace.html', contex)


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
                return redirect('workspace')
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






