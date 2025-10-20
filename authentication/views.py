"""
Views for authentication app handling user registration, login, and verification.
"""

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from .forms import SignUpForm, CustomAuthenticationForm, VerificationForm
from .models import User, EmailVerification


def signup_view(request):
    """
    Handle user registration with email domain validation.
    
    GET: Display registration form
    POST: Process registration and send verification email
    """
    # Redirect to home if user is already authenticated
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            # Create user but don't activate yet
            user = form.save(commit=False)
            user.is_active = False  # Deactivate until email is verified
            user.save()
            
            # Create and send verification code
            verification = EmailVerification.objects.create(user=user)
            
            # Send verification email
            subject = 'Verify your email - Demo App'
            message = f'''
            Hello {user.username},
            
            Your verification code is: {verification.code}
            
            This code will expire in 30 minutes.
            
            If you didn't request this, please ignore this email.
            '''
            
            try:
                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [user.email],
                    fail_silently=False,
                )
                messages.success(
                    request, 
                    'Registration successful! Check your email for verification code.'
                )
                # Store user ID in session for verification
                request.session['pending_user_id'] = user.id
                return redirect('verify')
                
            except Exception as e:
                # If email fails, delete the user and show error
                user.delete()
                messages.error(
                    request, 
                    'Failed to send verification email. Please try again.'
                )
    else:
        form = SignUpForm()
    
    return render(request, 'authentication/signup.html', {'form': form})


def verify_view(request):
    """
    Handle email verification process.
    
    GET: Display verification code form
    POST: Validate code and activate user account
    """
    # Check if there's a pending user
    pending_user_id = request.session.get('pending_user_id')
    if not pending_user_id:
        messages.error(request, 'No pending verification.')
        return redirect('signup')
    
    try:
        user = User.objects.get(id=pending_user_id)
    except User.DoesNotExist:
        messages.error(request, 'Invalid verification session.')
        return redirect('signup')
    
    if request.method == 'POST':
        form = VerificationForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            
            # Check for valid verification code
            verification = EmailVerification.objects.filter(
                user=user,
                code=code,
                is_used=False
            ).first()
            
            if verification and verification.is_valid():
                # Mark verification as used
                verification.is_used = True
                verification.save()
                
                # Activate and verify user
                user.is_active = True
                user.is_verified = True
                user.save()
                
                # Clear session
                del request.session['pending_user_id']
                
                # Log user in
                login(request, user)
                messages.success(request, 'Email verified successfully!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid or expired verification code.')
    else:
        form = VerificationForm()
    
    return render(request, 'authentication/verify.html', {
        'form': form,
        'email': user.email
    })


def login_view(request):
    """
    Handle user login with email and password.
    
    GET: Display login form
    POST: Authenticate user and redirect to home
    """
    # Redirect to home if user is already authenticated
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            
            # Check if user is verified
            if not user.is_verified:
                messages.error(
                    request, 
                    'Please verify your email before logging in.'
                )
                # Resend verification
                request.session['pending_user_id'] = user.id
                return redirect('verify')
            
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            
            # Redirect to next URL or home
            next_url = request.GET.get('next', 'home')
            return redirect(next_url)
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'authentication/login.html', {'form': form})


@login_required
def home_view(request):
    """
    Display home page for authenticated users.
    
    Requires user to be logged in.
    """
    return render(request, 'home.html', {'user': request.user})


@login_required
def logout_view(request):
    """
    Log out the current user and redirect to login page.
    """
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('login')