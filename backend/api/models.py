"""
Models for Chemical Equipment Parameter Visualizer.
Defines Dataset (upload session) and Equipment (individual records) models.
"""
from django.db import models
from django.contrib.auth.models import User
import json


class Dataset(models.Model):
    """
    Represents a single CSV upload session.
    Stores metadata and computed summary statistics.
    The application keeps only the last 5 datasets per user.
    """
    # Link to the user who uploaded this dataset
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='datasets')
    
    # Original filename for reference
    filename = models.CharField(max_length=255)
    
    # When this dataset was uploaded
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # Summary statistics stored as JSON for flexibility
    # Contains: total_count, avg_flowrate, avg_pressure, avg_temperature, type_distribution
    summary_json = models.TextField(default='{}')
    
    class Meta:
        # Order by most recent first
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.filename} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def summary(self):
        """Parse and return the summary as a dictionary."""
        return json.loads(self.summary_json)
    
    @summary.setter
    def summary(self, value):
        """Store the summary dictionary as JSON."""
        self.summary_json = json.dumps(value)
    
    def save(self, *args, **kwargs):
        """
        Override save to enforce the 5-dataset limit per user.
        After saving, delete older datasets beyond the limit.
        """
        super().save(*args, **kwargs)
        
        # Keep only the last 5 datasets for this user
        user_datasets = Dataset.objects.filter(user=self.user).order_by('-uploaded_at')
        datasets_to_delete = user_datasets[5:]  # Get all beyond first 5
        
        # Delete old datasets and their associated equipment records
        for old_dataset in datasets_to_delete:
            old_dataset.delete()


class Equipment(models.Model):
    """
    Represents a single piece of chemical equipment.
    Each equipment belongs to a Dataset (upload session).
    """
    # Link to parent dataset - cascade delete when dataset is removed
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='equipment')
    
    # Equipment name from CSV (e.g., "Pump-1", "Valve-2")
    name = models.CharField(max_length=255)
    
    # Equipment type/category (e.g., "Pump", "Compressor", "Valve")
    equipment_type = models.CharField(max_length=100)
    
    # Operational parameters - using FloatField for decimal precision
    flowrate = models.FloatField(help_text="Flow rate in appropriate units")
    pressure = models.FloatField(help_text="Pressure in appropriate units")
    temperature = models.FloatField(help_text="Temperature in appropriate units")
    
    class Meta:
        # Order alphabetically by name within a dataset
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.equipment_type})"
