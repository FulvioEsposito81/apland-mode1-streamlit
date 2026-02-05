"""
Configuration settings for the Geotechnical Application
"""
import os

# API Configuration
API_BASE_URL = os.environ.get("API_URL", "http://localhost:8000")  # Change this to your API server URL

# API Endpoints
ENDPOINTS = {
    "sfd": "/functions/sfd/",
    "compute": "/functions/computation/"
}

# Application Settings
APP_TITLE = "MODEI"
APP_VERSION = "1.0.0.9"

# Calculation Settings
AUTO_CALCULATE_SFD = True  # Automatically calculate SFd when geometric/mechanical parameters change
SFD_DEBOUNCE_SECONDS = 1.0  # Wait time before triggering SFd calculation after parameter change
