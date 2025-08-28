# src/django_example/apps/middleware.py

# Middleware order is important. These will typically be added to the
# end of the default MIDDLEWARE list in settings.py.
PROJECT_MIDDLEWARE = [
    # 'corsheaders.middleware.CorsMiddleware',
    # 'apps.core.middleware.MyCustomMiddleware',
]