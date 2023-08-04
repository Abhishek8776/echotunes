from django.db import models
from base.models import BaseModel

# Create your models here.


class Banner(BaseModel):
  image = models.ImageField(upload_to='banner/')
