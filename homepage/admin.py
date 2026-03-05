from django.contrib import admin

from .models import Patient, PatientServiceEvent, Service


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')
    search_fields = ('name',)


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('id', 'emri', 'mjeku', 'created_by', 'updated_by', 'data')
    search_fields = ('emri', 'mjeku', 'email', 'nr_cel')


@admin.register(PatientServiceEvent)
class PatientServiceEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'patient', 'service', 'service_date', 'price', 'created_by', 'created_at')
    list_filter = ('service', 'service_date', 'created_at')
    search_fields = ('patient__emri', 'service__name', 'price', 'created_by__username')
