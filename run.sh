#!/data/data/com.termux/files/usr/bin/bash

echo "Starting Package Tracking System..."
echo "=================================="

# Check if Python is installed
if ! command -v python &> /dev/null; then
    echo "Python is not installed. Installing..."
    pkg install python -y
fi

# Install dependencies
echo "Installing dependencies..."
pip install flask flask-cors --quiet

# Create necessary directories
mkdir -p static/images templates

# Check if data file exists
if [ ! -f "tracking_data.json" ]; then
    echo "Creating default data file..."
    python -c "
import json
from datetime import datetime
data = {
    'tracking_ids': {
        'AB123CDE45': {
            'name': 'Sandra Beasley-Lawson',
            'address': '811 Robin Circle',
            'city': 'Hattiesburg',
            'state': 'MS',
            'zip': '39402',
            'status': 'In Transit',
            'locations': [{'city': 'Berlin, Germany', 'lat': 52.5200, 'long': 13.4050}],
            'created_at': str(datetime.now()),
            'last_updated': str(datetime.now())
        }
    }
}
with open('tracking_data.json', 'w') as f:
    json.dump(data, f, indent=4)
"
fi

# Get local IP address
IP=$(ifconfig wlan0 | grep "inet " | awk '{print $2}')
if [ -z "$IP" ]; then
    IP="127.0.0.1"
fi

echo ""
echo "System Information:"
echo "-------------------"
echo "Local URL: https://tracking-system-7.onrender.com"
echo "Admin Panel: https://tracking-system-7.onrender.com/admin"
echo ""
echo "Default Login Credentials:"
echo "Username: admin"
echo "Password: admin123"
echo ""
echo "Sample Tracking IDs:"
echo "AB123CDE45, JGD987WQTR, BLMN654KJI"
echo ""
echo "Press Ctrl+C to stop the server"
echo "=================================="

# Run the server
python server.py
