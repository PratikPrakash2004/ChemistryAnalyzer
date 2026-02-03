"""
Admin configuration for Chemical Equipment models.
Allows administrators to view and manage datasets through Django admin.
"""
from django.contrib import admin
from .models import Dataset, Equipment


class EquipmentInline(admin.TabularInline):
    """
    Inline display of Equipment within Dataset admin.
    Shows equipment records directly in the dataset detail page.
    """
    model = Equipment
    extra = 0  # Don't show empty forms for new records
    readonly_fields = ['name', 'equipment_type', 'flowrate', 'pressure', 'temperature']


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    """
    Admin configuration for Dataset model.
    """
    list_display = ['filename', 'user', 'uploaded_at', 'equipment_count']
    list_filter = ['user', 'uploaded_at']
    search_fields = ['filename', 'user__username']
    readonly_fields = ['summary_json', 'uploaded_at']
    inlines = [EquipmentInline]
    
    def equipment_count(self, obj):
        """Display the number of equipment records in this dataset."""
        return obj.equipment.count()
    equipment_count.short_description = 'Equipment Count'


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    """
    Admin configuration for Equipment model.
    """
    list_display = ['name', 'equipment_type', 'flowrate', 'pressure', 'temperature', 'dataset']
    list_filter = ['equipment_type', 'dataset']
    search_fields = ['name', 'equipment_type']
