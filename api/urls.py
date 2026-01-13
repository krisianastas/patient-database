from django.urls import path

from . import views

urlpatterns = [
    path('patients/', views.patients_collection, name='api-patients'),
    path('patients/<int:pk>/', views.patient_detail, name='api-patient-detail'),
]
