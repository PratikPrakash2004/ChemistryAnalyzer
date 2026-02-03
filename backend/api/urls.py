"""
URL patterns for the Chemical Equipment API.
Defines all API endpoints for authentication, upload, datasets, and reports.
"""
from django.urls import path
from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    CSVUploadView,
    DatasetListView,
    DatasetDetailView,
    GeneratePDFReportView,
)

urlpatterns = [
    # Authentication endpoints
    path('auth/register/', RegisterView.as_view(), name='register'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/logout/', LogoutView.as_view(), name='logout'),
    
    # CSV Upload endpoint
    path('upload/', CSVUploadView.as_view(), name='csv-upload'),
    
    # Dataset endpoints
    path('datasets/', DatasetListView.as_view(), name='dataset-list'),
    path('datasets/<int:pk>/', DatasetDetailView.as_view(), name='dataset-detail'),
    path('datasets/<int:pk>/report/', GeneratePDFReportView.as_view(), name='dataset-report'),
]
