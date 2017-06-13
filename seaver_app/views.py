# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os import path

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Workspace, File as FileModel
from .forms import SignUpForm, FileUploadForm
from django.contrib.auth import login, authenticate, logout

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

    context = {'workspaces': workspaces}

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
    workspace.full_clean()
    # cambia la data di ultima modifica
    workspace.save()

    file_upload_form = FileUploadForm(request.POST, request.FILES)

    if file_upload_form.is_valid():
        file_model = FileModel()
        file_model.workspace = workspace
        file_model.name = file_upload_form.cleaned_data['name']
        file_uploaded = file_upload_form.cleaned_data['file']

        # todo leggere correttamente il file
        # file_model.save()

        # restituisco il modello di file vuoto
        file_upload_form = FileUploadForm()

    contex = {'wname': workspace.name,
              'form_action': request.path,
              'file_upload_form': file_upload_form}

    return render(request, 'seaver_app/workspace.html', contex)


def signup(request):
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






