"""
Views for the Chemical Equipment API.
Handles CSV upload, data analysis, PDF generation, and authentication.
"""
import io
import json
import logging
from datetime import datetime

import numpy as np
import pandas as pd
from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework.parsers import MultiPartParser, FormParser
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER

def _to_native(obj):
    """Convert numpy scalar types to native Python for JSON serialization."""
    if isinstance(obj, dict):
        return {_to_native(k): _to_native(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_native(x) for x in obj]
    if isinstance(obj, (np.integer, np.int64, np.int32)):
        return int(obj)
    if isinstance(obj, (np.floating, np.float64, np.float32)):
        val = float(obj)
        return None if np.isnan(val) else val
    return obj


from .models import Dataset, Equipment
from .serializers import (
    DatasetListSerializer, DatasetDetailSerializer,
    UserSerializer, RegisterSerializer, LoginSerializer
)


class RegisterView(APIView):
    """
    POST /api/auth/register/
    Create a new user account and return an auth token.
    No authentication required for this endpoint.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            # Create auth token for immediate login after registration
            token, _ = Token.objects.get_or_create(user=user)
            
            return Response({
                'message': 'User registered successfully',
                'user': UserSerializer(user).data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    POST /api/auth/login/
    Authenticate user and return auth token.
    No authentication required for this endpoint.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            
            # Attempt to authenticate the user
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # Get or create token for this user
                token, _ = Token.objects.get_or_create(user=user)
                
                return Response({
                    'message': 'Login successful',
                    'user': UserSerializer(user).data,
                    'token': token.key
                })
            else:
                return Response({
                    'error': 'Invalid username or password'
                }, status=status.HTTP_401_UNAUTHORIZED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    """
    POST /api/auth/logout/
    Invalidate the user's auth token.
    Requires authentication.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Delete the user's token to log them out
        request.user.auth_token.delete()
        return Response({'message': 'Logged out successfully'})


class CSVUploadView(APIView):
    """
    POST /api/upload/
    Upload a CSV file, parse it, compute statistics, and store in database.
    Returns the computed summary and dataset ID.
    Requires authentication.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        # Check if file was provided
        if 'file' not in request.FILES:
            return Response({
                'error': 'No file provided. Please upload a CSV file.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        csv_file = request.FILES['file']
        
        # Validate file type
        if not csv_file.name.endswith('.csv'):
            return Response({
                'error': 'Invalid file type. Please upload a CSV file.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Read CSV using pandas - it handles the parsing automatically
            # Decode the uploaded file bytes to string for pandas
            df = pd.read_csv(io.StringIO(csv_file.read().decode('utf-8')))
            
            # Validate required columns exist
            required_columns = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                return Response({
                    'error': f'Missing required columns: {", ".join(missing_columns)}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Compute summary statistics using pandas
            summary = {
                'total_count': len(df),
                'avg_flowrate': round(df['Flowrate'].mean(), 2),
                'avg_pressure': round(df['Pressure'].mean(), 2),
                'avg_temperature': round(df['Temperature'].mean(), 2),
                # Group by Type and count occurrences
                'type_distribution': df['Type'].value_counts().to_dict(),
                # Additional stats for richer visualization
                'min_flowrate': round(df['Flowrate'].min(), 2),
                'max_flowrate': round(df['Flowrate'].max(), 2),
                'min_pressure': round(df['Pressure'].min(), 2),
                'max_pressure': round(df['Pressure'].max(), 2),
                'min_temperature': round(df['Temperature'].min(), 2),
                'max_temperature': round(df['Temperature'].max(), 2),
                # Averages by type for detailed charts
                'avg_by_type': df.groupby('Type').agg({
                    'Flowrate': 'mean',
                    'Pressure': 'mean',
                    'Temperature': 'mean'
                }).round(2).to_dict()
            }
            
            # Convert numpy types to native Python so summary is JSON-serializable
            summary = _to_native(summary)

            # Create the dataset record
            dataset = Dataset.objects.create(
                user=request.user,
                filename=csv_file.name,
            )
            dataset.summary = summary  # This uses the property setter
            dataset.save()
            
            # Create equipment records for each row in the CSV
            equipment_objects = []
            for _, row in df.iterrows():
                equipment_objects.append(Equipment(
                    dataset=dataset,
                    name=row['Equipment Name'],
                    equipment_type=row['Type'],
                    flowrate=row['Flowrate'],
                    pressure=row['Pressure'],
                    temperature=row['Temperature']
                ))
            
            # Bulk create for efficiency
            Equipment.objects.bulk_create(equipment_objects)
            
            return Response({
                'message': 'CSV uploaded and processed successfully',
                'dataset_id': dataset.id,
                'filename': csv_file.name,
                'summary': summary
            }, status=status.HTTP_201_CREATED)
            
        except pd.errors.EmptyDataError:
            return Response({
                'error': 'The CSV file is empty'
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logging.exception('CSV upload failed')
            return Response({
                'error': f'Error processing CSV: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


class DatasetListView(generics.ListAPIView):
    """
    GET /api/datasets/
    List all datasets for the authenticated user (last 5).
    Returns summary info without full equipment data.
    Requires authentication.
    """
    serializer_class = DatasetListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only return datasets belonging to the current user
        return Dataset.objects.filter(user=self.request.user)


class DatasetDetailView(generics.RetrieveAPIView):
    """
    GET /api/datasets/<id>/
    Get detailed view of a specific dataset including all equipment.
    Requires authentication and ownership of the dataset.
    """
    serializer_class = DatasetDetailSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        # Only allow access to user's own datasets
        return Dataset.objects.filter(user=self.request.user)


class GeneratePDFReportView(APIView):
    """
    GET /api/datasets/<id>/report/
    Generate and download a PDF report for a specific dataset.
    Includes summary statistics and equipment table.
    Requires authentication and ownership of the dataset.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        # Try to fetch the dataset
        try:
            dataset = Dataset.objects.get(pk=pk, user=request.user)
        except Dataset.DoesNotExist:
            return Response({
                'error': 'Dataset not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Create PDF in memory
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
        
        # Container for PDF elements
        elements = []
        
        # Get styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=20,
            alignment=TA_CENTER,
            spaceAfter=30,
            textColor=colors.HexColor('#1a56db')  # Blue theme color
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            textColor=colors.HexColor('#1e40af')
        )
        normal_style = styles['Normal']
        
        # Title
        elements.append(Paragraph("Chemical Equipment Parameter Report", title_style))
        elements.append(Paragraph(f"ChemEquipViz - Generated Report", styles['Normal']))
        elements.append(Spacer(1, 20))
        
        # Dataset Info
        elements.append(Paragraph("Dataset Information", heading_style))
        elements.append(Paragraph(f"<b>Filename:</b> {dataset.filename}", normal_style))
        elements.append(Paragraph(f"<b>Uploaded:</b> {dataset.uploaded_at.strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
        elements.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", normal_style))
        elements.append(Spacer(1, 20))
        
        # Summary Statistics
        summary = dataset.summary
        elements.append(Paragraph("Summary Statistics", heading_style))
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Equipment Count', str(summary.get('total_count', 'N/A'))],
            ['Average Flowrate', f"{summary.get('avg_flowrate', 'N/A')}"],
            ['Average Pressure', f"{summary.get('avg_pressure', 'N/A')}"],
            ['Average Temperature', f"{summary.get('avg_temperature', 'N/A')}"],
        ]
        
        summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a56db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f7ff')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#93c5fd')),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 20))
        
        # Type Distribution
        elements.append(Paragraph("Equipment Type Distribution", heading_style))
        type_dist = summary.get('type_distribution', {})
        type_data = [['Equipment Type', 'Count']]
        for eq_type, count in type_dist.items():
            type_data.append([eq_type, str(count)])
        
        type_table = Table(type_data, colWidths=[3*inch, 2*inch])
        type_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#059669')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecfdf5')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#6ee7b7')),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('PADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(type_table)
        elements.append(Spacer(1, 20))
        
        # Equipment Data Table
        elements.append(Paragraph("Equipment Details", heading_style))
        equipment_list = dataset.equipment.all()
        
        eq_data = [['Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']]
        for eq in equipment_list:
            eq_data.append([
                eq.name,
                eq.equipment_type,
                str(eq.flowrate),
                str(eq.pressure),
                str(eq.temperature)
            ])
        
        eq_table = Table(eq_data, colWidths=[1.5*inch, 1.3*inch, 1*inch, 1*inch, 1.1*inch])
        eq_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#7c3aed')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f5f3ff')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#c4b5fd')),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('PADDING', (0, 0), (-1, -1), 6),
            # Alternate row colors
            *[('BACKGROUND', (0, i), (-1, i), colors.white) for i in range(2, len(eq_data), 2)]
        ]))
        elements.append(eq_table)
        
        # Build PDF
        doc.build(elements)
        
        # Prepare response
        buffer.seek(0)
        response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="report_{dataset.filename}_{dataset.id}.pdf"'
        
        return response
