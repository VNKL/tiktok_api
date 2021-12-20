from django.contrib.auth.models import User as DjangoUser
from django.db import models


class User(DjangoUser):
    balance = models.IntegerField(default=0)
    is_admin = models.BooleanField(default=False)
    have_access = models.BooleanField(default=False)

    def __str__(self):
        return f'User "{self.username}"'
