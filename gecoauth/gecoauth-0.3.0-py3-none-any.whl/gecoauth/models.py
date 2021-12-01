from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model

# Create your models here.
class GecoUser(models.Model):
    
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    user_dir = models.CharField(max_length=150, unique=True)