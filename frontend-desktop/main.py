"""
ChemEquipViz - Desktop Application
Chemical Equipment Parameter Visualizer

This PyQt5 desktop application provides the same functionality as the web frontend,
connecting to the same Django backend. It allows users to:
1. Login/Register with the backend
2. Upload CSV files with chemical equipment data
3. View summary statistics and visualizations
4. Browse upload history
5. Download PDF reports

The application uses:
- PyQt5 for the GUI framework
- Matplotlib for data visualization (embedded in PyQt5)
- Requests library for API communication
"""

import sys
import os
import json
import requests
from datetime import datetime

# PyQt5 imports for GUI components
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox, QStackedWidget, QFrame, QGridLayout,
    QHeaderView, QSplitter, QGroupBox, QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon

# Matplotlib imports for charts
import matplotlib
matplotlib.use('Qt5Agg')  # Use Qt5 backend for matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

# ========== Configuration ==========

# API base URL - same backend as the web frontend
API_BASE_URL = "http://localhost:8000/api"

# Color theme (Blue - Version A)
COLORS = {
    'primary': '#2563eb',
    'primary_dark': '#1e40af',
    'primary_light': '#dbeafe',
    'success': '#10b981',
    'warning': '#f59e0b',
    'error': '#ef4444',
    'gray_50': '#f9fafb',
    'gray_100': '#f3f4f6',
    'gray_200': '#e5e7eb',
    'gray_500': '#6b7280',
    'gray_700': '#374151',
    'gray_800': '#1f2937',
    'white': '#ffffff',
}


# ========== API Service Class ==========

class APIService:
    """
    Handles all communication with the Django backend.
    Similar to the api.js service in the React frontend.
    """
    
    def __init__(self):
        self.token = None
        self.user = None
    
    def _headers(self):
        """Get headers for API requests, including auth token if available."""
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Token {self.token}'
        return headers
    
    def register(self, username, email, password):
        """Register a new user."""
        response = requests.post(
            f"{API_BASE_URL}/auth/register/",
            json={'username': username, 'email': email, 'password': password}
        )
        response.raise_for_status()
        data = response.json()
        self.token = data['token']
        self.user = data['user']
        return data
    
    def login(self, username, password):
        """Login an existing user."""
        response = requests.post(
            f"{API_BASE_URL}/auth/login/",
            json={'username': username, 'password': password}
        )
        response.raise_for_status()
        data = response.json()
        self.token = data['token']
        self.user = data['user']
        return data
    
    def logout(self):
        """Logout the current user."""
        if self.token:
            try:
                requests.post(
                    f"{API_BASE_URL}/auth/logout/",
                    headers=self._headers()
                )
            except:
                pass  # Ignore errors on logout
        self.token = None
        self.user = None
    
    def upload_csv(self, filepath):
        """Upload a CSV file to the backend."""
        headers = {}
        if self.token:
            headers['Authorization'] = f'Token {self.token}'
        
        with open(filepath, 'rb') as f:
            files = {'file': (os.path.basename(filepath), f, 'text/csv')}
            response = requests.post(
                f"{API_BASE_URL}/upload/",
                files=files,
                headers=headers
            )
        response.raise_for_status()
        return response.json()
    
    def get_datasets(self):
        """Get list of datasets."""
        response = requests.get(
            f"{API_BASE_URL}/datasets/",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()
    
    def get_dataset_detail(self, dataset_id):
        """Get details of a specific dataset."""
        response = requests.get(
            f"{API_BASE_URL}/datasets/{dataset_id}/",
            headers=self._headers()
        )
        response.raise_for_status()
        return response.json()
    
    def download_pdf_report(self, dataset_id, save_path):
        """Download PDF report for a dataset."""
        response = requests.get(
            f"{API_BASE_URL}/datasets/{dataset_id}/report/",
            headers=self._headers()
        )
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            f.write(response.content)
        return save_path


# Global API service instance
api = APIService()


# ========== Custom Widgets ==========

class StyledButton(QPushButton):
    """A styled button with consistent appearance."""
    
    def __init__(self, text, color='primary', parent=None):
        super().__init__(text, parent)
        self.color = color
        self.setMinimumHeight(40)
        self.setCursor(Qt.PointingHandCursor)
        self.apply_style()
    
    def apply_style(self):
        """Apply color-coded styling."""
        colors = {
            'primary': (COLORS['primary'], COLORS['primary_dark'], 'white'),
            'success': (COLORS['success'], '#059669', 'white'),
            'danger': (COLORS['error'], '#dc2626', 'white'),
            'secondary': (COLORS['gray_200'], COLORS['gray_200'], COLORS['gray_700']),
        }
        bg, hover, text = colors.get(self.color, colors['primary'])
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg};
                color: {text};
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background-color: {hover};
            }}
            QPushButton:disabled {{
                background-color: {COLORS['gray_200']};
                color: {COLORS['gray_500']};
            }}
        """)


class StatCard(QFrame):
    """A card widget for displaying a single statistic."""
    
    def __init__(self, title, value, color=COLORS['primary'], parent=None):
        super().__init__(parent)
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['white']};
                border-radius: 8px;
                border-left: 4px solid {color};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        
        # Value label (large)
        value_label = QLabel(str(value))
        value_label.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {COLORS['gray_800']};
        """)
        layout.addWidget(value_label)
        
        # Title label (small)
        title_label = QLabel(title)
        title_label.setStyleSheet(f"""
            font-size: 12px;
            color: {COLORS['gray_500']};
            text-transform: uppercase;
        """)
        layout.addWidget(title_label)


class MatplotlibCanvas(FigureCanvas):
    """A Matplotlib canvas widget for embedding charts in PyQt5."""
    
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        
        # Set figure background
        self.fig.patch.set_facecolor(COLORS['white'])


# ========== Login Page ==========

class LoginPage(QWidget):
    """Login/Register page widget."""
    
    def __init__(self, on_login_success):
        super().__init__()
        self.on_login_success = on_login_success
        self.is_registering = False
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the login page UI."""
        # Main layout with centered content
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignCenter)
        
        # Card container
        card = QFrame()
        card.setFixedWidth(400)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['white']};
                border-radius: 12px;
            }}
        """)
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(40, 40, 40, 40)
        card_layout.setSpacing(16)
        
        # Title
        title = QLabel("🧪 ChemEquipViz")
        title.setStyleSheet(f"""
            font-size: 28px;
            font-weight: bold;
            color: {COLORS['primary']};
        """)
        title.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title)
        
        # Subtitle
        subtitle = QLabel("Chemical Equipment Parameter Visualizer")
        subtitle.setStyleSheet(f"color: {COLORS['gray_500']}; font-size: 14px;")
        subtitle.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(subtitle)
        
        card_layout.addSpacing(20)
        
        # Error label (hidden by default)
        self.error_label = QLabel()
        self.error_label.setStyleSheet(f"""
            background-color: #fef2f2;
            color: #991b1b;
            padding: 10px;
            border-radius: 6px;
            border: 1px solid #fecaca;
        """)
        self.error_label.setWordWrap(True)
        self.error_label.hide()
        card_layout.addWidget(self.error_label)
        
        # Username field
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")
        self.username_input.setStyleSheet(self._input_style())
        card_layout.addWidget(self.username_input)
        
        # Email field (for registration)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email")
        self.email_input.setStyleSheet(self._input_style())
        self.email_input.hide()
        card_layout.addWidget(self.email_input)
        
        # Password field
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(self._input_style())
        self.password_input.returnPressed.connect(self.handle_submit)
        card_layout.addWidget(self.password_input)
        
        card_layout.addSpacing(10)
        
        # Submit button
        self.submit_btn = StyledButton("Sign In", 'primary')
        self.submit_btn.clicked.connect(self.handle_submit)
        card_layout.addWidget(self.submit_btn)
        
        # Toggle link
        self.toggle_btn = QPushButton("Don't have an account? Register")
        self.toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background: none;
                border: none;
                color: {COLORS['primary']};
                text-decoration: underline;
            }}
            QPushButton:hover {{
                color: {COLORS['primary_dark']};
            }}
        """)
        self.toggle_btn.setCursor(Qt.PointingHandCursor)
        self.toggle_btn.clicked.connect(self.toggle_mode)
        card_layout.addWidget(self.toggle_btn)
        
        main_layout.addWidget(card)
        
        # Set page background
        self.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:1,
                    stop:0 {COLORS['primary']},
                    stop:1 {COLORS['primary_dark']}
                );
            }}
        """)
    
    def _input_style(self):
        """Return consistent input field styling."""
        return f"""
            QLineEdit {{
                padding: 12px;
                font-size: 14px;
                border: 1px solid {COLORS['gray_200']};
                border-radius: 6px;
                background: {COLORS['white']};
            }}
            QLineEdit:focus {{
                border: 2px solid {COLORS['primary']};
            }}
        """
    
    def toggle_mode(self):
        """Toggle between login and registration mode."""
        self.is_registering = not self.is_registering
        self.error_label.hide()
        
        if self.is_registering:
            self.email_input.show()
            self.submit_btn.setText("Create Account")
            self.toggle_btn.setText("Already have an account? Sign in")
        else:
            self.email_input.hide()
            self.submit_btn.setText("Sign In")
            self.toggle_btn.setText("Don't have an account? Register")
    
    def handle_submit(self):
        """Handle form submission."""
        username = self.username_input.text().strip()
        password = self.password_input.text()
        email = self.email_input.text().strip()
        
        if not username or not password:
            self.show_error("Please fill in all required fields")
            return
        
        if self.is_registering and not email:
            self.show_error("Please provide an email address")
            return
        
        self.submit_btn.setEnabled(False)
        self.submit_btn.setText("Please wait...")
        
        try:
            if self.is_registering:
                api.register(username, email, password)
            else:
                api.login(username, password)
            
            self.on_login_success()
            
        except requests.exceptions.HTTPError as e:
            if e.response is not None:
                try:
                    error_data = e.response.json()
                    if 'error' in error_data:
                        self.show_error(error_data['error'])
                    elif 'username' in error_data:
                        self.show_error(f"Username: {error_data['username'][0]}")
                    else:
                        self.show_error("An error occurred. Please try again.")
                except:
                    self.show_error("An error occurred. Please try again.")
            else:
                self.show_error("Unable to connect to server.")
        except requests.exceptions.ConnectionError:
            self.show_error("Unable to connect to server. Is the backend running?")
        except Exception as e:
            self.show_error(str(e))
        finally:
            self.submit_btn.setEnabled(True)
            self.submit_btn.setText("Create Account" if self.is_registering else "Sign In")
    
    def show_error(self, message):
        """Display an error message."""
        self.error_label.setText(message)
        self.error_label.show()


# ========== Dashboard Page ==========

class DashboardPage(QWidget):
    """Main dashboard page with upload, stats, and charts."""
    
    def __init__(self):
        super().__init__()
        self.current_data = None
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the dashboard UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("Dashboard")
        header.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {COLORS['gray_800']};")
        layout.addWidget(header)
        
        # Upload section
        upload_card = QFrame()
        upload_card.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['white']};
                border-radius: 8px;
                border: 2px dashed {COLORS['gray_200']};
            }}
        """)
        upload_layout = QVBoxLayout(upload_card)
        upload_layout.setContentsMargins(30, 30, 30, 30)
        upload_layout.setAlignment(Qt.AlignCenter)
        
        # Upload icon and text
        upload_icon = QLabel("📁")
        upload_icon.setStyleSheet("font-size: 48px;")
        upload_icon.setAlignment(Qt.AlignCenter)
        upload_layout.addWidget(upload_icon)
        
        upload_text = QLabel("Click to upload a CSV file")
        upload_text.setStyleSheet(f"font-size: 16px; color: {COLORS['gray_700']};")
        upload_text.setAlignment(Qt.AlignCenter)
        upload_layout.addWidget(upload_text)
        
        upload_hint = QLabel("Supported format: CSV with columns (Equipment Name, Type, Flowrate, Pressure, Temperature)")
        upload_hint.setStyleSheet(f"font-size: 12px; color: {COLORS['gray_500']};")
        upload_hint.setAlignment(Qt.AlignCenter)
        upload_hint.setWordWrap(True)
        upload_layout.addWidget(upload_hint)
        
        upload_layout.addSpacing(10)
        
        self.upload_btn = StyledButton("Select CSV File", 'primary')
        self.upload_btn.clicked.connect(self.handle_upload)
        upload_layout.addWidget(self.upload_btn, alignment=Qt.AlignCenter)
        
        # Status label
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.hide()
        upload_layout.addWidget(self.status_label)
        
        layout.addWidget(upload_card)
        
        # Stats container (hidden until data is uploaded)
        self.stats_container = QWidget()
        stats_layout = QHBoxLayout(self.stats_container)
        stats_layout.setSpacing(16)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        self.stats_container.hide()
        layout.addWidget(self.stats_container)
        
        # Charts container (hidden until data is uploaded)
        self.charts_container = QWidget()
        charts_layout = QHBoxLayout(self.charts_container)
        charts_layout.setSpacing(16)
        charts_layout.setContentsMargins(0, 0, 0, 0)
        self.charts_container.hide()
        layout.addWidget(self.charts_container)
        
        # Table container (hidden until data is uploaded)
        self.table_container = QFrame()
        self.table_container.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['white']};
                border-radius: 8px;
            }}
        """)
        table_layout = QVBoxLayout(self.table_container)
        
        table_header = QLabel("Equipment Data")
        table_header.setStyleSheet(f"""
            font-size: 18px;
            font-weight: bold;
            color: {COLORS['gray_800']};
            padding: 16px;
            border-bottom: 1px solid {COLORS['gray_200']};
        """)
        table_layout.addWidget(table_header)
        
        self.data_table = QTableWidget()
        self.data_table.setStyleSheet(f"""
            QTableWidget {{
                border: none;
                gridline-color: {COLORS['gray_200']};
            }}
            QHeaderView::section {{
                background-color: {COLORS['primary']};
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }}
            QTableWidget::item {{
                padding: 8px;
            }}
        """)
        table_layout.addWidget(self.data_table)
        
        self.table_container.hide()
        layout.addWidget(self.table_container)
        
        # Add stretch to push everything up
        layout.addStretch()
    
    def handle_upload(self):
        """Handle CSV file upload."""
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV File",
            "",
            "CSV Files (*.csv)"
        )
        
        if not filepath:
            return
        
        self.upload_btn.setEnabled(False)
        self.upload_btn.setText("Uploading...")
        self.status_label.setText("Processing file...")
        self.status_label.setStyleSheet(f"color: {COLORS['gray_500']};")
        self.status_label.show()
        
        try:
            result = api.upload_csv(filepath)
            self.current_data = result
            
            # Fetch full dataset details
            dataset_detail = api.get_dataset_detail(result['dataset_id'])
            
            self.status_label.setText(f"✓ Successfully uploaded {result['filename']}")
            self.status_label.setStyleSheet(f"color: {COLORS['success']}; font-weight: bold;")
            
            # Update UI with data
            self.display_data(result['summary'], dataset_detail.get('equipment', []))
            
        except requests.exceptions.HTTPError as e:
            error_msg = "Upload failed"
            if e.response is not None:
                try:
                    error_data = e.response.json()
                    error_msg = error_data.get('error', error_msg)
                except:
                    pass
            self.status_label.setText(f"✗ {error_msg}")
            self.status_label.setStyleSheet(f"color: {COLORS['error']}; font-weight: bold;")
        except Exception as e:
            self.status_label.setText(f"✗ Error: {str(e)}")
            self.status_label.setStyleSheet(f"color: {COLORS['error']}; font-weight: bold;")
        finally:
            self.upload_btn.setEnabled(True)
            self.upload_btn.setText("Select CSV File")
    
    def display_data(self, summary, equipment):
        """Display the uploaded data in stats, charts, and table."""
        # Clear previous widgets
        for i in reversed(range(self.stats_container.layout().count())):
            self.stats_container.layout().itemAt(i).widget().setParent(None)
        
        for i in reversed(range(self.charts_container.layout().count())):
            self.charts_container.layout().itemAt(i).widget().setParent(None)
        
        # Add stat cards
        stats_layout = self.stats_container.layout()
        stats_layout.addWidget(StatCard("Total Equipment", summary['total_count'], COLORS['primary']))
        stats_layout.addWidget(StatCard("Avg Flowrate", summary['avg_flowrate'], COLORS['success']))
        stats_layout.addWidget(StatCard("Avg Pressure", summary['avg_pressure'], COLORS['warning']))
        stats_layout.addWidget(StatCard("Avg Temperature", summary['avg_temperature'], COLORS['error']))
        self.stats_container.show()
        
        # Create charts
        charts_layout = self.charts_container.layout()
        
        # Bar chart
        bar_canvas = MatplotlibCanvas(self, width=6, height=4)
        if summary.get('avg_by_type'):
            types = list(summary['avg_by_type']['Flowrate'].keys())
            flowrates = list(summary['avg_by_type']['Flowrate'].values())
            pressures = list(summary['avg_by_type']['Pressure'].values())
            temperatures = list(summary['avg_by_type']['Temperature'].values())
            
            x = range(len(types))
            width = 0.25
            
            bar_canvas.axes.bar([i - width for i in x], flowrates, width, label='Flowrate', color='#2563eb')
            bar_canvas.axes.bar(x, pressures, width, label='Pressure', color='#10b981')
            bar_canvas.axes.bar([i + width for i in x], temperatures, width, label='Temperature', color='#f59e0b')
            
            bar_canvas.axes.set_xlabel('Equipment Type')
            bar_canvas.axes.set_ylabel('Average Value')
            bar_canvas.axes.set_title('Average Parameters by Equipment Type')
            bar_canvas.axes.set_xticks(x)
            bar_canvas.axes.set_xticklabels(types, rotation=45, ha='right')
            bar_canvas.axes.legend()
            bar_canvas.fig.tight_layout()
        
        bar_frame = QFrame()
        bar_frame.setStyleSheet(f"background-color: {COLORS['white']}; border-radius: 8px;")
        bar_layout = QVBoxLayout(bar_frame)
        bar_layout.addWidget(bar_canvas)
        charts_layout.addWidget(bar_frame)
        
        # Pie chart
        pie_canvas = MatplotlibCanvas(self, width=5, height=4)
        if summary.get('type_distribution'):
            labels = list(summary['type_distribution'].keys())
            sizes = list(summary['type_distribution'].values())
            colors_list = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4']
            
            pie_canvas.axes.pie(sizes, labels=labels, colors=colors_list[:len(labels)],
                               autopct='%1.1f%%', startangle=90)
            pie_canvas.axes.set_title('Equipment Type Distribution')
        
        pie_frame = QFrame()
        pie_frame.setStyleSheet(f"background-color: {COLORS['white']}; border-radius: 8px;")
        pie_layout = QVBoxLayout(pie_frame)
        pie_layout.addWidget(pie_canvas)
        charts_layout.addWidget(pie_frame)
        
        self.charts_container.show()
        
        # Populate table
        self.data_table.setColumnCount(5)
        self.data_table.setHorizontalHeaderLabels(['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature'])
        self.data_table.setRowCount(len(equipment))
        
        for row, eq in enumerate(equipment):
            self.data_table.setItem(row, 0, QTableWidgetItem(eq['name']))
            self.data_table.setItem(row, 1, QTableWidgetItem(eq['equipment_type']))
            self.data_table.setItem(row, 2, QTableWidgetItem(str(eq['flowrate'])))
            self.data_table.setItem(row, 3, QTableWidgetItem(str(eq['pressure'])))
            self.data_table.setItem(row, 4, QTableWidgetItem(str(eq['temperature'])))
        
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table_container.show()


# ========== History Page ==========

class HistoryPage(QWidget):
    """History page showing last 5 uploaded datasets."""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the history page UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header with refresh button
        header_layout = QHBoxLayout()
        header = QLabel("Upload History")
        header.setStyleSheet(f"font-size: 24px; font-weight: bold; color: {COLORS['gray_800']};")
        header_layout.addWidget(header)
        header_layout.addStretch()
        
        refresh_btn = StyledButton("🔄 Refresh", 'secondary')
        refresh_btn.clicked.connect(self.load_data)
        header_layout.addWidget(refresh_btn)
        
        layout.addLayout(header_layout)
        
        # Info box
        info_label = QLabel("📋 Showing your last 5 uploaded datasets. Older uploads are automatically removed.")
        info_label.setStyleSheet(f"""
            background-color: {COLORS['primary_light']};
            color: {COLORS['primary_dark']};
            padding: 12px;
            border-radius: 6px;
        """)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Scroll area for history items
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        self.history_container = QWidget()
        self.history_layout = QVBoxLayout(self.history_container)
        self.history_layout.setSpacing(12)
        self.history_layout.setAlignment(Qt.AlignTop)
        
        scroll.setWidget(self.history_container)
        layout.addWidget(scroll)
        
        # Load data on init
        self.load_data()
    
    def load_data(self):
        """Load datasets from the API."""
        # Clear existing items
        for i in reversed(range(self.history_layout.count())):
            widget = self.history_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        
        try:
            datasets = api.get_datasets()
            
            if not datasets:
                empty_label = QLabel("No uploads yet. Upload a CSV file from the Dashboard to see it here.")
                empty_label.setStyleSheet(f"color: {COLORS['gray_500']}; padding: 40px;")
                empty_label.setAlignment(Qt.AlignCenter)
                self.history_layout.addWidget(empty_label)
            else:
                for dataset in datasets:
                    self.add_history_item(dataset)
                    
        except Exception as e:
            error_label = QLabel(f"Failed to load history: {str(e)}")
            error_label.setStyleSheet(f"color: {COLORS['error']}; padding: 20px;")
            self.history_layout.addWidget(error_label)
    
    def add_history_item(self, dataset):
        """Add a single history item to the list."""
        item = QFrame()
        item.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS['white']};
                border-radius: 8px;
            }}
            QFrame:hover {{
                background-color: {COLORS['gray_50']};
            }}
        """)
        
        item_layout = QHBoxLayout(item)
        item_layout.setContentsMargins(16, 12, 16, 12)
        
        # Info section
        info_layout = QVBoxLayout()
        
        filename = QLabel(f"📄 {dataset['filename']}")
        filename.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {COLORS['gray_800']};")
        info_layout.addWidget(filename)
        
        # Format date
        upload_date = datetime.fromisoformat(dataset['uploaded_at'].replace('Z', '+00:00'))
        date_str = upload_date.strftime('%Y-%m-%d %H:%M')
        
        meta = QLabel(f"Uploaded: {date_str} • {dataset['equipment_count']} equipment records")
        meta.setStyleSheet(f"color: {COLORS['gray_500']}; font-size: 12px;")
        info_layout.addWidget(meta)
        
        # Summary stats
        if dataset.get('summary'):
            summary = dataset['summary']
            stats_text = f"Avg Flow: {summary.get('avg_flowrate', 'N/A')} • Avg Pressure: {summary.get('avg_pressure', 'N/A')} • Avg Temp: {summary.get('avg_temperature', 'N/A')}"
            stats_label = QLabel(stats_text)
            stats_label.setStyleSheet(f"""
                background-color: {COLORS['gray_100']};
                color: {COLORS['gray_700']};
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 11px;
            """)
            info_layout.addWidget(stats_label)
        
        item_layout.addLayout(info_layout)
        item_layout.addStretch()
        
        # Action buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        pdf_btn = StyledButton("📥 PDF", 'success')
        pdf_btn.clicked.connect(lambda checked, d=dataset: self.download_pdf(d))
        btn_layout.addWidget(pdf_btn)
        
        item_layout.addLayout(btn_layout)
        
        self.history_layout.addWidget(item)
    
    def download_pdf(self, dataset):
        """Download PDF report for a dataset."""
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF Report",
            f"report_{dataset['filename']}.pdf",
            "PDF Files (*.pdf)"
        )
        
        if not save_path:
            return
        
        try:
            api.download_pdf_report(dataset['id'], save_path)
            QMessageBox.information(self, "Success", f"PDF saved to:\n{save_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to download PDF:\n{str(e)}")


# ========== Main Window ==========

class MainWindow(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ChemEquipViz - Chemical Equipment Visualizer")
        self.setMinimumSize(1200, 800)
        
        # Set application-wide style
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COLORS['gray_50']};
            }}
        """)
        
        # Create stacked widget for page switching
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)
        
        # Create pages
        self.login_page = LoginPage(self.on_login_success)
        self.main_page = None
        
        # Start with login page
        self.stack.addWidget(self.login_page)
        self.stack.setCurrentWidget(self.login_page)
    
    def on_login_success(self):
        """Called when user successfully logs in."""
        # Create main page with navbar and content
        self.main_page = QWidget()
        main_layout = QVBoxLayout(self.main_page)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Navbar
        navbar = QFrame()
        navbar.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(
                    x1:0, y1:0, x2:1, y2:0,
                    stop:0 {COLORS['primary']},
                    stop:1 {COLORS['primary_dark']}
                );
            }}
        """)
        navbar.setFixedHeight(60)
        navbar_layout = QHBoxLayout(navbar)
        navbar_layout.setContentsMargins(20, 0, 20, 0)
        
        # App title
        title = QLabel("🧪 ChemEquipViz")
        title.setStyleSheet("color: white; font-size: 20px; font-weight: bold;")
        navbar_layout.addWidget(title)
        
        navbar_layout.addStretch()
        
        # Navigation buttons
        self.dashboard_btn = QPushButton("Dashboard")
        self.dashboard_btn.setStyleSheet(self._nav_btn_style())
        self.dashboard_btn.setCursor(Qt.PointingHandCursor)
        self.dashboard_btn.clicked.connect(lambda: self.show_page(0))
        navbar_layout.addWidget(self.dashboard_btn)
        
        self.history_btn = QPushButton("History")
        self.history_btn.setStyleSheet(self._nav_btn_style())
        self.history_btn.setCursor(Qt.PointingHandCursor)
        self.history_btn.clicked.connect(lambda: self.show_page(1))
        navbar_layout.addWidget(self.history_btn)
        
        navbar_layout.addSpacing(20)
        
        # User info
        user_label = QLabel(f"Welcome, {api.user['username']}")
        user_label.setStyleSheet("color: #bfdbfe;")
        navbar_layout.addWidget(user_label)
        
        logout_btn = StyledButton("Logout", 'secondary')
        logout_btn.clicked.connect(self.logout)
        navbar_layout.addWidget(logout_btn)
        
        main_layout.addWidget(navbar)
        
        # Content area
        self.content_stack = QStackedWidget()
        self.dashboard_page = DashboardPage()
        self.history_page = HistoryPage()
        self.content_stack.addWidget(self.dashboard_page)
        self.content_stack.addWidget(self.history_page)
        
        main_layout.addWidget(self.content_stack)
        
        # Add main page to stack and show it
        self.stack.addWidget(self.main_page)
        self.stack.setCurrentWidget(self.main_page)
    
    def _nav_btn_style(self):
        """Return styling for navigation buttons."""
        return f"""
            QPushButton {{
                background: transparent;
                color: #bfdbfe;
                border: none;
                padding: 8px 16px;
                font-size: 14px;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.1);
                color: white;
                border-radius: 4px;
            }}
        """
    
    def show_page(self, index):
        """Switch to a different page."""
        self.content_stack.setCurrentIndex(index)
        
        # Refresh history when switching to it
        if index == 1:
            self.history_page.load_data()
    
    def logout(self):
        """Log out the current user."""
        api.logout()
        
        # Remove main page and show login
        self.stack.removeWidget(self.main_page)
        self.main_page = None
        
        # Create fresh login page
        self.login_page = LoginPage(self.on_login_success)
        self.stack.addWidget(self.login_page)
        self.stack.setCurrentWidget(self.login_page)


# ========== Entry Point ==========

def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    
    # Set application metadata
    app.setApplicationName("ChemEquipViz")
    app.setApplicationDisplayName("Chemical Equipment Visualizer")
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run the application event loop
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
