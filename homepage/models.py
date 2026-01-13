from django.db import models

class Patient(models.Model):
    emri = models.CharField(max_length=191, null=True)
    nr_cel = models.CharField(max_length=50, null=True)
    email = models.EmailField(max_length=191, null=True)
    mjeku = models.CharField(max_length=191, null=True)
    cmimi = models.CharField(max_length=50, null=True)
    sherbimet = models.TextField(null=True)
    data = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.emri