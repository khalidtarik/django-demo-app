"""
Main URL configuration for demo_project.
"""

from django.contrib import admin
from django.urls import path, include
from authentication.views import home_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home_view, name='home'),
    path('home/', home_view, name='home'),
    path('auth/', include('authentication.urls')),
]
