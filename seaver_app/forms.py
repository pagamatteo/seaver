# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import PunctualAnnotation, IntervalAnnotation


class SignUpForm(UserCreationForm):
    email = forms.EmailField(max_length=254, help_text='Required. Inform a valid email address.')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2',)


class FileUploadForm(forms.Form):
    file = forms.FileField(label='File to be uploaded')


class WorkspaceForm(forms.Form):
    workspace_name = forms.CharField(max_length=50, required=True)



class AnnotationTypeForm(forms.Form):
    name = forms.CharField(max_length=50, required=True, label="Name")
    description = forms.CharField(widget=forms.Textarea, label="Description")
