from django.urls import path

from . import views

urlpatterns = [
    path('auth/session/', views.auth_session, name='api-auth-session'),
    path('auth/login/', views.auth_login, name='api-auth-login'),
    path('auth/logout/', views.auth_logout, name='api-auth-logout'),
    path('patients/', views.patients_collection, name='api-patients'),
    path('patients/<int:pk>/', views.patient_detail, name='api-patient-detail'),
]
