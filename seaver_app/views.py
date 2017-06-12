# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from os import path

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Workspace


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

    return render(request, 'workspace_show.html', context)


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

    contex = {'wname': workspace.name}

    return render(request, 'workspace.html', contex)




