# src/django_example/core/views.py

from django.http import HttpResponse

def home(request):
    """A simple view to confirm the app is working."""
    return HttpResponse("<h1>Hello, World! The 'core' app is working.</h1>")