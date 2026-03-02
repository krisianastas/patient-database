from django.contrib import admin

from .models import Patient, Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('id', 'emri', 'mjeku', 'created_by', 'updated_by', 'data')
    search_fields = ('emri', 'mjeku', 'email', 'nr_cel')
