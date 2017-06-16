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
from . import views, apis_views
from django.contrib.auth import views as auth_views
from .apis import router as api_router

urlpatterns = [
    url(r'^workspace/$', views.show_workspaces, name='workspace'),
    url(r'^create_workspace/$', views.create_empty_workspace, name='create_workspace'),
    url(r'workspace/(?P<name>\w+)/$', views.open_workspace),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^login/$', auth_views.login, {'template_name': 'seaver_app/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'template_name': 'seaver_app/logged_out.html'}, name='logout'),
    url(r'^apis/', include(api_router.urls)),
    url(r'^apis/file', apis_views.FileView.as_view())
]
