from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    username = models.CharField(max_length=100, unique=True, null=True, blank=True)
    first_name = models.CharField(max_length=50, null=False)
    last_name = models.CharField(max_length=50, null=False)
    email = models.EmailField(max_length=200, unique=True)
    password = models.CharField(max_length=150,null=False)
    street = models.TextField(("Street"), max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    house_number = models.CharField(max_length=10, null=True, blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos', null=True, blank=True)
    is_checked = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'password']

    def __str__(self):
        return f"{self.get_full_name()}"


class Reset_password(models.Model):
    user_id = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=10, unique=True)
    expired_at = models.DateTimeField()
    
    def __str__(self):
        return f"{self.user_id}"

class CodesVerification(models.Model):
    changePasswordCode = models.CharField(max_length=10,unique=True)
    user = models.ForeignKey(CustomUser, null=True, on_delete=models.SET_NULL) 
    def __str__(self):
        return f"{self.user}"
