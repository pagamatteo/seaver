"""seaver URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from rest_framework import routers
from . import views, apis_views
from django.contrib.auth import views as auth_views

urlpatterns = [
    url(r'^workspace/$', views.show_workspaces, name='workspaces'),
    url(r'^create_workspace/$', views.create_empty_workspace, name='create_workspace'),
    url(r'^delete_workspace/(?P<workspace_name>\w+( \w+)*)/$', views.delete_workspace, name='delete_workspace'),
    url(r'^workspace/(?P<name>\w+( \w+)*)/$', views.open_workspace, name='workspace'),
    url(r'^workspace/(?P<name>\w+( \w+)*)/export/$', views.workspace_export_view, name='workspace_export'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^login/$', auth_views.login, {'template_name': 'seaver_app/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'seaver_app/logged_out.html'}, name='logout'),
    url(r'^apis/', include(apis_views.router.urls)),
    url(r'^apis/file-upload/$', apis_views.FileUploadedView.as_view()),
    url(r'^apis/field-data/(?P<pk>[0-9]+)/$', apis_views.FieldDataView.as_view(), name='fielddata-detail'),
    url(r'^apis/analysis/(?P<pk>[0-9]+)/$', apis_views.AnalysisView.as_view(), name='analysis-detail'),
    #url(r'workspace/(?P<name>\w+( \w+)*)/create_file/$', views.create_empty_workspace, name='create_file'),
    url(r'^workspace/(?P<workspace_name>\w+( \w+)*)/delete_file/(?P<file_name>.+)/$', views.delete_file, name='delete_file'),
]
