# src/django_example/apps/installed_apps.py

# Add your project's applications here.
# Using the AppConfig is the modern and recommended way.
PROJECT_APPS = [
    'apps.core.apps.CoreConfig',
    # 'users.apps.UsersConfig',
    # 'products.apps.ProductsConfig',
]

# You can also list third-party apps here to keep settings clean.
THIRD_PARTY_APPS = [
    # 'rest_framework',
    # 'corsheaders',
]