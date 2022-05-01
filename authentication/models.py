from pyexpat import model
from django.db import models

# Create your models here.


class Password(models.Model):
    website = models.CharField(max_length=100)
    user_password = models.CharField(max_length=200)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.website
