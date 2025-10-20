"""
Custom User model and related models for authentication app.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
import random
import string
from datetime import datetime, timedelta
from django.utils import timezone


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Adds email verification functionality.
    """
    email = models.EmailField(unique=True, verbose_name='Email Address')
    is_verified = models.BooleanField(
        default=False,
        help_text='Indicates whether the user has verified their email'
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def __str__(self):
        return self.email


class EmailVerification(models.Model):
    """
    Model to store email verification codes.
    """
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='verifications'
    )
    code = models.CharField(
        max_length=6,
        help_text='6-digit verification code'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        """
        Override save method to generate code and set expiration.
        """
        if not self.code:
            self.code = self.generate_code()
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=30)
        super().save(*args, **kwargs)
    
    @staticmethod
    def generate_code():
        """
        Generate a random 6-digit verification code.
        
        Returns:
            str: 6-digit code
        """
        return ''.join(random.choices(string.digits, k=6))
    
    def is_valid(self):
        """
        Check if the verification code is still valid.
        
        Returns:
            bool: True if valid, False otherwise
        """
        return not self.is_used and self.expires_at > timezone.now()