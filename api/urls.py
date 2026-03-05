from django.urls import path

from . import views

urlpatterns = [
    path('auth/session/', views.auth_session, name='api-auth-session'),
    path('auth/login/', views.auth_login, name='api-auth-login'),
    path('auth/logout/', views.auth_logout, name='api-auth-logout'),
    path('services/', views.services_collection, name='api-services'),
    path('patients/', views.patients_collection, name='api-patients'),
    path('patients/<int:pk>/', views.patient_detail, name='api-patient-detail'),
    path(
        'patients/<int:pk>/service-events/',
        views.patient_service_events_collection,
        name='api-patient-service-events',
    ),
    path(
        'patients/<int:pk>/service-events/<int:event_id>/',
        views.patient_service_event_detail,
        name='api-patient-service-event-detail',
    ),
]
