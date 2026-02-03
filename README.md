#ChemEqualizer

## 📋 Project Overview

ChemEqualizer is a hybrid web and desktop application for visualizing chemical equipment parameters. It allows users to upload CSV files containing equipment data, view summary statistics, and generate visual charts for data analysis.


## 🛠️ Tech Stack

- **Backend**: Django 4.2 + Django REST Framework
- **Web Frontend**: React.js + Chart.js
- **Desktop Frontend**: PyQt5 + Matplotlib
- **Database**: SQLite
- **Authentication**: Token-based (DRF TokenAuthentication)
- **PDF Generation**: ReportLab

## 📁 Project Structure

```
ChemEquipViz/
├── backend/                 # Django REST API
│   ├── chemviz/            # Django project settings
│   ├── api/                # Main API application
│   ├── manage.py
│   └── requirements.txt
├── frontend-web/           # React web application
│   ├── public/
│   ├── src/
│   └── package.json
├── frontend-desktop/       # PyQt5 desktop application
│   ├── main.py
│   └── requirements.txt
├── sample_equipment_data.csv
└── README.md
```

## ✨ Features

1. **User Authentication** - Register/Login with token-based auth
2. **CSV Upload** - Upload equipment data in CSV format
3. **Data Summary** - Automatic calculation of statistics (averages, counts)
4. **Visualizations** - Bar charts and Pie charts for data analysis
5. **History** - View last 5 uploaded datasets
6. **PDF Reports** - Generate downloadable PDF reports
7. **Dual Frontend** - Both web and desktop applications

## 🚀 Setup Instructions

### Prerequisites

Make sure you have installed:
- Python 3.8 or higher
- Node.js 16 or higher
- npm (comes with Node.js)
- Git

### Step 1: Clone/Download the Project

```bash
# If using Git
git clone <your-repo-url>
cd ChemEquipViz
```

### Step 2: Backend Setup

Open a terminal and run these commands:

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate

# Create a superuser (optional - for admin access)
python manage.py createsuperuser

# Start the backend server
python manage.py runserver
```

The backend will start at: **http://localhost:8000**

Keep this terminal open and running.

### Step 3: Web Frontend Setup

Open a NEW terminal window:

```bash
# Navigate to frontend-web directory
cd frontend-web

# Install Node.js dependencies
npm install

# Start the React development server
npm start
```

The web app will start at: **http://localhost:3000**

Keep this terminal open and running.

### Step 4: Desktop Frontend Setup

Open a NEW terminal window:

```bash
# Navigate to frontend-desktop directory
cd frontend-desktop

# Install Python dependencies (if not using same venv as backend)
pip install -r requirements.txt

# Run the desktop application
python main.py
```

## 📊 CSV File Format

The application expects CSV files with the following columns:

| Column Name | Description | Example |
|-------------|-------------|---------|
| Equipment Name | Unique identifier | Pump-1 |
| Type | Equipment category | Pump, Valve, Compressor, etc. |
| Flowrate | Flow rate value | 120.5 |
| Pressure | Pressure value | 15.2 |
| Temperature | Temperature value | 85.0 |

### Sample CSV Content:
```csv
Equipment Name,Type,Flowrate,Pressure,Temperature
Pump-1,Pump,120.5,15.2,85
Pump-2,Pump,135.0,16.8,90
Valve-1,Valve,80.3,12.1,75
```

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register/` | POST | Register new user |
| `/api/auth/login/` | POST | Login user |
| `/api/auth/logout/` | POST | Logout user |
| `/api/upload/` | POST | Upload CSV file |
| `/api/datasets/` | GET | List all datasets (last 5) |
| `/api/datasets/<id>/` | GET | Get dataset details |
| `/api/datasets/<id>/report/` | GET | Download PDF report |

## 📝 Usage Guide

1. **Register/Login**: Create an account or login with existing credentials
2. **Upload CSV**: Click "Select CSV File" or drag-and-drop a CSV file
3. **View Data**: See summary statistics and visualizations
4. **History**: Check your last 5 uploads in the History tab
5. **Download Report**: Click "PDF Report" to download a formatted report

## 👤 Author

Pratik Prakash
Pratik17432@gmail.com

---
