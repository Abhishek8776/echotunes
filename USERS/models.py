from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin
from . manager import CustomUserManager
from django.db import models
import uuid


class User(AbstractBaseUser, PermissionsMixin):
  id = models.TextField(primary_key=True,default=uuid.uuid4,editable=False)
  email = models.EmailField(unique=True)
  name=models.CharField(max_length=200 , null=True)
  is_active = models.BooleanField('access',default=True)
  is_staff = models.BooleanField(default=False)
  date_joined = models.DateTimeField(auto_now_add=True)  # Add this line


  objects = CustomUserManager()

  USERNAME_FIELD = 'email'
  REQUIRED_FIELDS = ['name']

  def __str__(self):
      return self.name
