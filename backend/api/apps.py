"""
App configuration for the API application.
"""
from django.apps import AppConfig


class ApiConfig(AppConfig):
    """Configuration for the Chemical Equipment API app."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'
    verbose_name = 'Chemical Equipment API'
