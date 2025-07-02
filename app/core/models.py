"""
Database models
"""

from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin)
from django.conf import settings
from django.db import models


# Create your models here.


class UserManager(BaseUserManager):
    """Manager for custom user model"""

    def create_user(self, email, password=None, **extra_fields):
        """
        Create save and return a new user
        **extra_fields is a special Python syntax that:
        Accepts any additional keyword arguments passed to the function.
        These are collected into a dictionary called extra_fields.
        for example: create_user(email="tobi@example.com", password="secure123", first_name="Tobi", is_staff=True)
        email → "tobi@example.com"
        password → "secure123"
        extra_fields → {"first_name": "Tobi", "is_staff": True}
        hence user = self.model(email=email, **extra_fields) becomes,
        user = self.model(email="tobi@example.com", first_name="Tobi", is_staff=True)
        """
        normalize_email = self.normalize_email(email)
        user = self.model(email=normalize_email, **extra_fields)
        if not email:
            raise ValueError("User must have an email address")
        # This hashes the password securely using Django's built-in system (encrypting the password)
        user.set_password(password)
        # Saves the user to the database. This tells Django which database to use if you have multiple databases
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and return a new superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


# AbstractBaseUser contains the functionality for the auth system, but no fields
# PermissionsMixin contains the functionality for Django permissions and fields
class User(AbstractBaseUser, PermissionsMixin):
    """User in the system"""
    email = models.EmailField(max_length=255, unique=True)
    name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    # assigns a user manager
    objects = UserManager()
    # Replaces the USERNAME default field in django with the email field. No longer requires a username
    USERNAME_FIELD = 'email'


class Recipe(models.Model):
    """Recipe Object"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    time_minutes = models.IntegerField()
    price = models.DecimalField(max_digits=5, decimal_places=2)
    link = models.CharField(max_length=255, blank=True)
    tags = models.ManyToManyField('Tag')  # Tags for filtering; many-to-many relationship with Tag model

    def __str__(self):
        return self.title


class Tag(models.Model):
    """Tag for filtering recipes"""

    name = models.CharField(max_length=255)

    # Links this tag to a user; deleting the user deletes their tags
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Reference the active user model
        on_delete=models.CASCADE,  # Cascade delete to clean up tags
    )

    def __str__(self):
        # Return the tag’s name when the object is converted to a string
        return self.name
