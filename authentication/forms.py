"""
Forms for user authentication and registration.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.conf import settings
from .models import User


class SignUpForm(UserCreationForm):
    """
    Custom user registration form that validates email domain.
    """
    email = forms.EmailField(
        max_length=255,
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address'
        })
    )
    
    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    
    def clean_email(self):
        """
        Validate that the email belongs to the allowed domain.
        
        Returns:
            str: Cleaned email address
            
        Raises:
            ValidationError: If email domain is not allowed
        """
        email = self.cleaned_data.get('email')
        if email:
            domain = email.split('@')[1] if '@' in email else ''
            if domain != settings.ALLOWED_EMAIL_DOMAIN:
                raise ValidationError(
                    f'Registration is only allowed for {settings.ALLOWED_EMAIL_DOMAIN} email addresses.'
                )
        return email


class CustomAuthenticationForm(AuthenticationForm):
    """
    Custom login form with Bootstrap styling.
    """
    username = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )


class VerificationForm(forms.Form):
    """
    Form for email verification code input.
    """
    code = forms.CharField(
        max_length=6,
        min_length=6,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter 6-digit code',
            'autocomplete': 'off'
        })
    )
    
    def clean_code(self):
        """
        Validate that the code contains only digits.
        
        Returns:
            str: Cleaned verification code
            
        Raises:
            ValidationError: If code is not numeric
        """
        code = self.cleaned_data.get('code')
        if code and not code.isdigit():
            raise ValidationError('Verification code must contain only digits.')
        return code