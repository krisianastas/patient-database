from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


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
    cmimi = models.CharField(max_length=50, null=True)
    services = models.ManyToManyField(Service, blank=True, related_name='patients')
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
