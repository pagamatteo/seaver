# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import csv

from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, Http404, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import ensure_csrf_cookie

from . import workspace_export
from .csvreader import FileToStrings, StringsToLines, CSVReader
from .forms import *
from .models import Workspace, File as FileModel, FileData, BulkWriter, FileFieldName


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
        files = FileModel.objects.filter(workspace=e)
        files = [file.name for file in files]
        workspaces.append({"workspace_name": e.name, "workspace_files": files})

    context = {
        'workspaces': workspaces,
        'username':user.username,
        'no_right_sidebar': True
    }

    return render(request, 'seaver_app/workspace_show.html', context)


@login_required()
@ensure_csrf_cookie
def open_workspace(request, name):
    """
    Apre o crea il workspace selezionato
    :param request:
    :param name: nome del workspace
    :return:
    """
    user = request.user

    try:
        workspace = Workspace.objects.get(user=user, name=name)
    except Workspace.DoesNotExist:
        raise Http404()

    # cambia la data di ultima modifica
    workspace.save()

    file_upload_form = FileUploadForm()
    annotation_type_form = AnnotationTypeForm()

    files = FileModel.objects.filter(workspace=workspace)
    files = [file.name for file in files]

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

            response = {'errors': False, 'results': {"file_pk": file_model.pk}}
            return JsonResponse(response)
    else:

        contex = {'wname': workspace.name,
                  'form_action': request.path,
                  'file_upload_form': file_upload_form,
                  'files': files,
                  'workspace': workspace,
                  'username': user.username,
                  'annotation_type_form': annotation_type_form,
                  }

        return render(request, 'seaver_app/workspace.html', contex)


@login_required()
def workspace_export_view(request, name):
    user = request.user

    try:
        workspace = Workspace.objects.get(user=user, name=name)
    except Workspace.DoesNotExist as e:
        raise Http404()

    # trasformo il workspace in un dataframe
    df = workspace_export.workspace_to_dataframe(workspace)

    # costruisco la risposta csv
    response = HttpResponse()
    response['content_type'] = 'txt/csv'
    response['Content-Disposition'] = 'attachment; filename="{}.csv"'.format(workspace.name)

    # creo il writer
    csv_writer = csv.writer(response)

    # output columns names
    columns = ['Index', ] + [c for c in df.columns]
    csv_writer.writerow(columns)

    # itero sopra il dataframe e stampo ogni riga
    for row in df.itertuples(name=None):
        csv_writer.writerow(row)

    return response


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
        if Workspace.objects.filter(user=user, name=workspace_name).exists():
            response = {'errors': True, 'results': {'workspace_name': ['Workspace name already exists']}}
            return JsonResponse(response)

        workspace = Workspace(user=user, name=workspace_name)
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
    :return:
    """

    response = {'errors': False}
    user = request.user

    try:
        workspace = Workspace.objects.filter(user=user, name=workspace_name).get()
    except Workspace.DoesNotExist:
        raise Http404()

    workspace.delete()
    return JsonResponse(response)
