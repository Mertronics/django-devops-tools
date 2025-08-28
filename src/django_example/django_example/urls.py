# src/django_example/django_example/urls.py

from django.contrib import admin
from django.urls import path, include  # <-- Make sure to import 'include'

urlpatterns = [
    path('admin/', admin.site.urls),
    # --- ADD THIS LINE ---
    # Any request that doesn't match 'admin/' will be sent to core.urls
    path('', include('core.urls')),
]