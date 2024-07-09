from django.db import models
from django.contrib.auth.models import User

def profile_picture_path(instance, filename):
    return f'profile_pictures/{instance.national_id}/{filename}'

class Citizens(models.Model):
    # map the citizen to the User model provided by Django
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='citizen')
    national_id = models.CharField(max_length=30, primary_key=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    date_of_birth = models.DateField()
    nationality = models.CharField(max_length=30)
    picture = models.ImageField(upload_to=profile_picture_path, default='default.png')
    SEX_CHOICES = [  # each one is written twice because the first one is the value and the second is what will appear in the dropdown menu
        ('M', 'Male'),
        ('F', 'Female'),
    ]
    sex = models.CharField(max_length=1, choices=SEX_CHOICES)

    BLOOD_TYPES = [
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    ]
    blood_type = models.CharField(max_length=3, choices=BLOOD_TYPES)

    def __str__(self):
        return self.user.username

class Addresses(models.Model):
    citizen = models.ForeignKey(Citizens, on_delete=models.CASCADE)
    country = models.CharField(max_length=30)
    city = models.CharField(max_length=30)
    street = models.CharField(max_length=30)
    building_number = models.IntegerField()
    floor_number = models.IntegerField()
    apartment_number = models.IntegerField()

    def __str__(self):
        return self.street + ', ' + self.city + ', ' + self.country

def passport_picture_path(instance, filename):
    return f'passport_pictures/{instance.citizen.national_id}/{filename}'

def request_picture_path(instance, filename):
    return f'requests_new_pictures/{instance.citizen.national_id}/{filename}'

def proof_document_path(instance, filename):
    return f'requests_doc_proof/{instance.citizen.national_id}/{filename}'

class Passports(models.Model):
    citizen = models.ForeignKey(Citizens, on_delete=models.CASCADE)
    passport_number = models.CharField(max_length=30, primary_key=True)
    issue_date = models.DateField()
    expiry_date = models.DateField()
    picture = models.ImageField(upload_to=passport_picture_path)

class RenewalRequests(models.Model):
    citizen = models.ForeignKey(Citizens, on_delete=models.CASCADE)
    request_type = models.CharField(max_length=30, choices=[("Passport", "Passport"), ["Driver's License", "Driver's License"]])
    picture = models.ImageField(upload_to=request_picture_path) # this is for the new doc
    reason = models.TextField()
    proof_document = models.FileField(upload_to=proof_document_path)
    status = models.CharField(max_length=30, choices=[("Pending", "Pending"), ("Approved", "Approved"), ("Rejected", "Rejected")], default="Pending")
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
