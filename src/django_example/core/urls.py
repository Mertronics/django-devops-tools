# src/django_example/core/urls.py

from django.urls import path
from . import views  # Import views from the current directory

app_name = 'core'  # Optional: for namespacing URLs

urlpatterns = [
    # When a request comes to the root (''), use the 'home' view
    path('', views.home, name='home'),
]