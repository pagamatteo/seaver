# -*- coding: utf-8 -*-
from rest_framework import permissions


# todo devo ancora capire se è utile
class IsOwner(permissions.IsAuthenticated):
    def has_object_permission(self, request, view, obj):

        return obj.owner == request.user