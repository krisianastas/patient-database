from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone


class Service(models.Model):
    name = models.CharField(max_length=191, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        self.name = (self.name or '').strip()
        if not self.name:
            raise ValidationError({'name': 'Service name is required.'})

        duplicate = Service.objects.filter(name__iexact=self.name)
        if self.pk:
            duplicate = duplicate.exclude(pk=self.pk)
        if duplicate.exists():
            raise ValidationError({'name': 'A service with this name already exists.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Patient(models.Model):
    emri = models.CharField(max_length=191, null=True)
    nr_cel = models.CharField(max_length=50, null=True)
    email = models.EmailField(max_length=191, null=True)
    mjeku = models.CharField(max_length=191, null=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='created_patients',
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='updated_patients',
    )
    data = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.emri or f'Patient {self.pk}'


class PatientServiceEvent(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='service_events')
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name='patient_events')
    service_date = models.DateField()
    price = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='created_service_events',
    )

    def clean(self):
        if not self.service_date:
            raise ValidationError({'service_date': 'Service date is required.'})
        if self.service_date > timezone.localdate():
            raise ValidationError({'service_date': 'Service date cannot be in the future.'})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.patient} - {self.service} ({self.service_date})'
