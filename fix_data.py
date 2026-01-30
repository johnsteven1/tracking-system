import json
import os
from datetime import datetime

DATA_FILE = 'tracking_data.json'

if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)
    
    print("Current data structure:")
    print(f"Keys: {list(data.keys())}")
    
    # Check if system_stats exists
    if 'system_stats' not in data:
        print("Adding missing system_stats...")
        tracking_ids = data.get('tracking_ids', {})
        
        data['system_stats'] = {
            'total_tracking_ids': len(tracking_ids),
            'active_shipments': sum(1 for t in tracking_ids.values() 
                                   if t.get('status', '') in ['In Transit', 'Processing', 'Out for Delivery']),
            'delivered_today': 0,
            'images_count': 0
        }
        
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        
        print("✅ system_stats added successfully!")
    else:
        print("✅ system_stats already exists!")
    
    print("\nCurrent stats:")
    print(json.dumps(data.get('system_stats', {}), indent=2))
    
    print(f"\nTotal tracking IDs: {len(data.get('tracking_ids', {}))}")
    print("Tracking IDs:", list(data.get('tracking_ids', {}).keys()))
    
else:
    print(f"❌ {DATA_FILE} not found! Creating default data...")
    default_data = {
        "tracking_ids": {
            "AB123CDE45": {
                "name": "Sandra Beasley-Lawson",
                "address": "811 Robin Circle",
                "city": "Hattiesburg",
                "state": "MS",
                "zip": "39402",
                "delivery_date": str(datetime.now().date()),
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
            "delivered_today": 0,
            "images_count": 0
        }
    }
    
    with open(DATA_FILE, 'w') as f:
        json.dump(default_data, f, indent=4)
    
    print("✅ Default data created successfully!")
