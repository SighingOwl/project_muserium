from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from .managers import UserManager

class User(AbstractBaseUser, PermissionsMixin):

    username = models.CharField(max_length=128, blank=True)
    email = models.EmailField(db_index=True, unique=True)
    mobile = models.CharField(max_length=13, blank=True)
    name = models.CharField(max_length=128, blank=True)
    postcode = models.CharField(max_length=10, blank=True)
    address = models.CharField(max_length=255, blank=True)
    address_detail = models.CharField(max_length=255, blank=True)
    address_extra = models.CharField(max_length=255, blank=True)

    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
