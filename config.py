import json
import os
from datetime import datetime

class Config:
    SECRET_KEY = 'your-secret-key-2024'  # Change this in production
    DATA_FILE = 'tracking_data.json'
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'
    
    @staticmethod
    def init_app(app):
        # Create necessary directories
        os.makedirs(Config.STATIC_FOLDER, exist_ok=True)
        os.makedirs(os.path.join(Config.STATIC_FOLDER, 'images'), exist_ok=True)
        os.makedirs(Config.TEMPLATES_FOLDER, exist_ok=True)
        
        # Initialize default data if needed
        Config.ensure_default_data()
    
    @staticmethod
    def ensure_default_data():
        if not os.path.exists(Config.DATA_FILE):
            print(f"Creating default data file: {Config.DATA_FILE}")
            default_data = {
                "tracking_ids": {
                    "AB123CDE45": {
                        "name": "Sandra Beasley-Lawson",
                        "address": "811 Robin Circle",
                        "city": "Hattiesburg",
                        "state": "MS",
                        "zip": "39402",
                        "status": "In Transit",
                        "locations": [
                            {"city": "Berlin, Germany", "lat": 52.5200, "long": 13.4050}
                        ],
                        "created_at": str(datetime.now()),
                        "last_updated": str(datetime.now())
                    }
                },
                "system_stats": {
                    "total_tracking_ids": 1,
                    "active_shipments": 1,
                    "delivered_today": 0
                }
            }
            
            with open(Config.DATA_FILE, 'w') as f:
                json.dump(default_data, f, indent=4)
    
    @staticmethod
    def get_sample_tracking_ids():
        return [
            "AB123CDE45",
            "JGD987WQTR", 
            "BLMN654KJI",
            "PKNN754KKI",
            "XYZ789ABC0",
            "DEF456GHI1",
            "JKL234MNO2",
            "PQR890STU3"
        ]
