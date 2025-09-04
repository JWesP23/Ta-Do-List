from django.db import models

# Create your models here.
class Member(models.Model):
    id = models.AutoField(primary_key=True)  # Primary Key
    username = models.CharField(max_length=100, unique=True)  #Unique Required
    email = models.EmailField(max_length=255, blank=True, null=True)  # Optional May run into issues for multiple users with the same email with not forcing uniqueness
    password_hash = models.TextField()  # Required