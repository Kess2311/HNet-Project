from django.contrib import admin
from . import models

admin.site.register(models.Hospital)
admin.site.register(models.TreatmentSession)
admin.site.register(models.Statistics)
