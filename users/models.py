from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework.authtoken.models import Token
from django.db.models.signals import post_save
from django.conf import settings
from django.dispatch import receiver


class User(AbstractUser):
    is_patient = models.BooleanField(default=False)
    is_doctor = models.BooleanField(default=False)
    birth_date = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)

    def __str__(self):
        return self.username


class EmergencyContact(models.Model):
    name = models.CharField(max_length=50)
    phone_number = models.CharField(max_length=20)
    relationship = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class Patient(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    emergency_contact = models.ForeignKey(EmergencyContact, on_delete=models.CASCADE, null=True, blank=True)
    height = models.IntegerField(null=True, blank=True)
    weight = models.IntegerField(null=True, blank=True)
    blood_type = models.CharField(max_length=10, null=True, blank=True)
    allergies = models.TextField(null=True, blank=True)
    medications = models.TextField(null=True, blank=True)
    general_health = models.CharField(null=True, blank=True)
    checkup = models.CharField(null=True, blank=True)
    exercise = models.BooleanField(default=False)
    heart_disease = models.BooleanField(default=False)
    skin_cancer = models.BooleanField(default=False)
    other_cancer = models.BooleanField(default=False)
    depression = models.BooleanField(default=False)
    diabetes = models.BooleanField(default=False)
    arthritis = models.BooleanField(default=False)
    sex = models.TextField(default=False)
    age_category = models.TextField(default=False)
    bmi = models.FloatField(default=False)
    smoking_history = models.BooleanField(default=False)
    alcohol_consumption = models.FloatField(default=False)
    fruit_consumption = models.FloatField(default=False)
    green_vegetable_consumption = models.FloatField(default=False)
    fried_potato_consumption = models.FloatField(default=False)

    def __str__(self):
        return self.user.username


class Doctor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    speciality = models.CharField(max_length=50, null=True, blank=True)
    background = models.TextField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    hospital = models.CharField(max_length=100, null=True, blank=True)
    patients = models.ManyToManyField(Patient, related_name='doctors', blank=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)
