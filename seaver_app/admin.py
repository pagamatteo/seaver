# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Workspace)
admin.site.register(File)
admin.site.register(FileFieldName)
admin.site.register(FileData)
admin.site.register(PunctualAnnotation)
admin.site.register(PunctualAnnotationEvent)
admin.site.register(IntervalAnnotation)
admin.site.register(IntervalAnnotationEvent)
