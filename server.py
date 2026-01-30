from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime
import random
import base64
from werkzeug.utils import secure_filename
import sys

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Auto-configure for Render.com deployment
def get_deployment_config():
    """Auto-detect deployment environment and configure accordingly"""
    is_render = 'RENDER' in os.environ
    is_railway = 'RAILWAY_STATIC_URL' in os.environ
    is_heroku = 'DYNO' in os.environ
    is_pythonanywhere = 'PYTHONANYWHERE_DOMAIN' in os.environ
    
    if is_render:
        print("🎯 Detected Render.com deployment")
        data_dir = os.getcwd()
        base_url = os.environ.get('RENDER_EXTERNAL_URL', 'http://localhost:5000')
    elif is_railway:
        print("🚂 Detected Railway.app deployment")
        data_dir = os.getcwd()
        base_url = os.environ.get('RAILWAY_STATIC_URL', 'http://localhost:5000')
    elif is_heroku:
        print("⚡ Detected Heroku deployment")
        data_dir = os.getcwd()
        base_url = f"https://{os.environ.get('HEROKU_APP_NAME', 'your-app')}.herokuapp.com"
    elif is_pythonanywhere:
        print("☁️ Detected PythonAnywhere deployment")
        data_dir = '/home/yourusername/tracking_system'
        base_url = f"https://{os.environ.get('PYTHONANYWHERE_DOMAIN', 'yourusername.pythonanywhere.com')}"
    else:
        print("💻 Local development mode")
        data_dir = os.getcwd()
        base_url = "http://localhost:5000"
    
    return {
        'data_dir': data_dir,
        'base_url': base_url.rstrip('/'),
        'is_production': any([is_render, is_railway, is_heroku, is_pythonanywhere])
    }

# Get deployment configuration
deploy_config = get_deployment_config()
DATA_DIR = deploy_config['data_dir']
BASE_URL = deploy_config['base_url']
IS_PRODUCTION = deploy_config['is_production']

print(f"📍 Data directory: {DATA_DIR}")
print(f"🌐 Base URL: {BASE_URL}")
print(f"🚀 Production mode: {IS_PRODUCTION}")

# File paths
DATA_FILE = os.path.join(DATA_DIR, 'tracking_data.json')
CONFIG_FILE = os.path.join(DATA_DIR, 'system_config.json')
UPLOAD_FOLDER = os.path.join(DATA_DIR, 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Create necessary directories
for folder in [UPLOAD_FOLDER, 'templates', 'static']:
    os.makedirs(folder, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_config():
    """Load system configuration"""
    default_config = {
        "default_location": {
            "city": "Berlin, Germany",
            "lat": 52.5200,
            "long": 13.4050
        },
        "company_name": "Smart Real-Time Package Tracking",
        "map_zoom_level": 12,
        "base_url": BASE_URL,
        "deployment_mode": "production" if IS_PRODUCTION else "development",
        "version": "2.0.0",
        "features": {
            "image_upload": True,
            "real_time_updates": True,
            "admin_dashboard": True,
            "location_config": True
        }
    }
    
    if not os.path.exists(CONFIG_FILE):
        print(f"📝 Creating new config file at: {CONFIG_FILE}")
        save_config(default_config)
        return default_config
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            # Update base_url if it's old
            if config.get('base_url') != BASE_URL:
                config['base_url'] = BASE_URL
                config['deployment_mode'] = "production" if IS_PRODUCTION else "development"
                save_config(config)
                print(f"🔄 Updated config with new base URL: {BASE_URL}")
            
            # Ensure new fields exist
            if 'version' not in config:
                config['version'] = "2.0.0"
            if 'features' not in config:
                config['features'] = default_config['features']
            
            return config
    except Exception as e:
        print(f"⚠️ Error loading config, using default: {e}")
        return default_config

def save_config(config):
    """Save system configuration"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except Exception as e:
        print(f"❌ Error saving config: {e}")
        return False

def load_data():
    """Load tracking data with automatic creation if needed"""
    if not os.path.exists(DATA_FILE):
        print(f"📦 Creating new tracking data file at: {DATA_FILE}")
        
        # Load system configuration for default location
        config = load_config()
        default_location = config.get('default_location', {
            "city": "Berlin, Germany", 
            "lat": 52.5200, 
            "long": 13.4050
        })
        
        # Default data structure with more sample tracking IDs
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
                    "locations": [default_location],
                    "created_at": str(datetime.now()),
                    "last_updated": str(datetime.now()),
                    "image_url": "/uploads/sample_package.jpg"
                },
                "JGD987WQTR": {
                    "name": "John Doe",
                    "address": "123 Main Street",
                    "city": "New York",
                    "state": "NY",
                    "zip": "10001",
                    "delivery_date": str(datetime.now().date()),
                    "status": "Processing",
                    "locations": [default_location],
                    "created_at": str(datetime.now()),
                    "last_updated": str(datetime.now())
                },
                "XYZ789ABCD": {
                    "name": "Jane Smith",
                    "address": "456 Oak Avenue",
                    "city": "Los Angeles",
                    "state": "CA",
                    "zip": "90001",
                    "delivery_date": str((datetime.now().replace(day=datetime.now().day + 3)).date()),
                    "status": "Out for Delivery",
                    "locations": [default_location],
                    "created_at": str(datetime.now()),
                    "last_updated": str(datetime.now())
                }
            },
            "system_stats": {
                "total_tracking_ids": 3,
                "active_shipments": 3,
                "delivered_today": 0,
                "images_count": 1,
                "last_updated": str(datetime.now())
            }
        }
        
        # Create a sample image file if it doesn't exist
        sample_image_path = os.path.join(UPLOAD_FOLDER, 'sample_package.jpg')
        if not os.path.exists(sample_image_path):
            try:
                # Create a simple placeholder image
                from PIL import Image, ImageDraw
                img = Image.new('RGB', (400, 300), color='lightblue')
                d = ImageDraw.Draw(img)
                d.text((100, 150), "Package\nSample\nImage", fill="darkblue", align="center")
                img.save(sample_image_path)
                print(f"📸 Created sample image at: {sample_image_path}")
            except Exception as e:
                print(f"⚠️ Could not create sample image: {e}")
        
        save_data(default_data)
        return default_data
    
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            
            # Ensure system_stats exists in old data
            if 'system_stats' not in data:
                data['system_stats'] = {
                    'total_tracking_ids': len(data.get('tracking_ids', {})),
                    'active_shipments': sum(1 for t in data.get('tracking_ids', {}).values() 
                                           if t.get('status', '') in ['In Transit', 'Processing', 'Out for Delivery']),
                    'delivered_today': sum(1 for t in data.get('tracking_ids', {}).values() 
                                          if t.get('status', '') == 'Delivered' and 
                                          t.get('last_updated', '').startswith(str(datetime.now().date()))),
                    'images_count': sum(1 for t in data.get('tracking_ids', {}).values() 
                                       if t.get('image_url') or t.get('image_base64') or t.get('has_image')),
                    'last_updated': str(datetime.now())
                }
                save_data(data)
                print("📊 Added system stats to existing data")
                
            # Update last_updated timestamp
            data['system_stats']['last_updated'] = str(datetime.now())
            
            return data
    except Exception as e:
        print(f"❌ Error loading data, creating new: {e}")
        return load_data()  # Recursive call to create new data

def save_data(data):
    """Save tracking data with error handling"""
    try:
        # Update stats before saving
        tracking_ids = data.get('tracking_ids', {})
        
        stats = data.get('system_stats', {})
        stats['total_tracking_ids'] = len(tracking_ids)
        stats['active_shipments'] = sum(
            1 for t in tracking_ids.values() 
            if t.get('status', '') in ['In Transit', 'Processing', 'Out for Delivery']
        )
        stats['delivered_today'] = sum(
            1 for t in tracking_ids.values() 
            if t.get('status', '') == 'Delivered' and 
            t.get('last_updated', '').startswith(str(datetime.now().date()))
        )
        stats['images_count'] = sum(
            1 for t in tracking_ids.values() 
            if t.get('image_url') or t.get('image_base64')
        )
        stats['last_updated'] = str(datetime.now())
        
        data['system_stats'] = stats
        
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=4)
        
        # Print debug info in development
        if not IS_PRODUCTION:
            print(f"💾 Saved data: {len(tracking_ids)} tracking IDs")
        
        return True
    except Exception as e:
        print(f"❌ Error saving data: {e}")
        return False

# Serve static files
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

# Serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    try:
        return send_from_directory(UPLOAD_FOLDER, filename)
    except:
        return jsonify({'error': 'File not found'}), 404

# Routes
@app.route('/')
def tracking_page():
    """Main tracking page"""
    config = load_config()
    return render_template('tracking.html', 
                         base_url=config.get('base_url', BASE_URL),
                         company_name=config.get('company_name', 'Package Tracking'),
                         version=config.get('version', '2.0.0'))

@app.route('/admin')
def admin_page():
    """Admin dashboard"""
    config = load_config()
    return render_template('admin_dashboard.html', 
                         base_url=config.get('base_url', BASE_URL),
                         company_name=config.get('company_name', 'Package Tracking'),
                         version=config.get('version', '2.0.0'))

@app.route('/admin/location')
def admin_location_page():
    """Location configuration page"""
    config = load_config()
    return render_template('admin_location.html', 
                         base_url=config.get('base_url', BASE_URL),
                         company_name=config.get('company_name', 'Package Tracking'),
                         default_location=config.get('default_location'))

# Health check endpoint for Render.com and other platforms
@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy', 
        'timestamp': str(datetime.now()),
        'version': '2.0.0',
        'data_file': os.path.exists(DATA_FILE),
        'config_file': os.path.exists(CONFIG_FILE),
        'uploads_folder': os.path.exists(UPLOAD_FOLDER),
        'tracking_ids_count': len(load_data().get('tracking_ids', {}))
    })

# System status endpoint
@app.route('/api/status', methods=['GET'])
def system_status():
    """System status information"""
    config = load_config()
    data = load_data()
    
    return jsonify({
        'system': {
            'version': config.get('version', '2.0.0'),
            'company_name': config.get('company_name', 'Package Tracking'),
            'base_url': config.get('base_url', BASE_URL),
            'deployment_mode': config.get('deployment_mode', 'development'),
            'uptime': str(datetime.now() - datetime.fromtimestamp(os.path.getctime(DATA_FILE)) if os.path.exists(DATA_FILE) else datetime.now())
        },
        'data': {
            'total_tracking_ids': len(data.get('tracking_ids', {})),
            'active_shipments': data.get('system_stats', {}).get('active_shipments', 0),
            'images_uploaded': data.get('system_stats', {}).get('images_count', 0),
            'last_updated': data.get('system_stats', {}).get('last_updated', str(datetime.now()))
        },
        'features': config.get('features', {})
    })

# System configuration endpoints
@app.route('/api/config', methods=['GET'])
def get_config():
    """Get system configuration"""
    config = load_config()
    return jsonify(config)

@app.route('/api/config/location', methods=['PUT'])
def update_location():
    """Update default location configuration"""
    # Verify admin access (simple token check)
    auth_header = request.headers.get('Authorization')
    if not auth_header or 'admin_token' not in auth_header:
        # Also accept token in request body for simplicity
        if not request.json.get('admin_token') == 'admin_token':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    location_data = request.json
    
    # Validate required fields
    required_fields = ['city', 'lat', 'long']
    if not all(field in location_data for field in required_fields):
        return jsonify({'success': False, 'error': 'Missing required fields: city, lat, long'}), 400
    
    # Validate coordinates
    try:
        lat = float(location_data['lat'])
        long = float(location_data['long'])
        
        if not (-90 <= lat <= 90):
            return jsonify({'success': False, 'error': 'Latitude must be between -90 and 90'}), 400
        if not (-180 <= long <= 180):
            return jsonify({'success': False, 'error': 'Longitude must be between -180 and 180'}), 400
            
    except ValueError:
        return jsonify({'success': False, 'error': 'Invalid coordinates. Must be numbers'}), 400
    
    config = load_config()
    config['default_location'] = {
        'city': location_data['city'],
        'lat': lat,
        'long': long
    }
    
    # Optionally update all existing tracking IDs to this location
    if location_data.get('update_existing', False):
        data = load_data()
        updated_count = 0
        for tracking_id in data['tracking_ids']:
            if data['tracking_ids'][tracking_id].get('locations'):
                data['tracking_ids'][tracking_id]['locations'][0] = config['default_location']
                updated_count += 1
        
        if updated_count > 0:
            save_data(data)
            print(f"📍 Updated location for {updated_count} tracking IDs")
    
    save_config(config)
    
    return jsonify({
        'success': True, 
        'message': 'Default location updated successfully',
        'location': config['default_location'],
        'updated_tracking_ids': location_data.get('update_existing', False)
    })

@app.route('/api/config', methods=['PUT'])
def update_config():
    """Update system configuration"""
    # Verify admin access
    auth_header = request.headers.get('Authorization')
    if not auth_header or 'admin_token' not in auth_header:
        if not request.json.get('admin_token') == 'admin_token':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    config_data = request.json
    config = load_config()
    
    # Update only allowed fields
    allowed_fields = ['default_location', 'company_name', 'map_zoom_level', 'features']
    for field in allowed_fields:
        if field in config_data:
            config[field] = config_data[field]
    
    save_config(config)
    
    return jsonify({
        'success': True, 
        'message': 'Configuration updated successfully',
        'config': config
    })

# API endpoints
@app.route('/api/tracking/<tracking_id>', methods=['GET'])
def get_tracking_info(tracking_id):
    """Get tracking information by ID"""
    data = load_data()
    
    if tracking_id in data['tracking_ids']:
        tracking_data = data['tracking_ids'][tracking_id]
        return jsonify({
            'success': True,
            **tracking_data
        })
    
    return jsonify({'success': False, 'error': 'Tracking ID not found'}), 404

@app.route('/api/tracking/<tracking_id>/status', methods=['GET'])
def get_tracking_status(tracking_id):
    """Get real-time tracking status with simulated movement"""
    data = load_data()
    
    if tracking_id in data['tracking_ids']:
        tracking_data = data['tracking_ids'][tracking_id]
        
        # Simulate real-time movement for packages in transit (only in development for testing)
        if not IS_PRODUCTION and tracking_data['status'] in ['In Transit', 'Processing', 'Out for Delivery']:
            # Add small random movement to location
            if tracking_data['locations']:
                current_location = tracking_data['locations'][0]
                new_lat = current_location['lat'] + random.uniform(-0.01, 0.01)
                new_long = current_location['long'] + random.uniform(-0.01, 0.01)
                
                # Keep within reasonable bounds
                new_lat = max(-90, min(90, new_lat))
                new_long = max(-180, min(180, new_long))
                
                tracking_data['locations'][0]['lat'] = round(new_lat, 4)
                tracking_data['locations'][0]['long'] = round(new_long, 4)
                tracking_data['last_updated'] = str(datetime.now())
            
            # Occasionally update status (only in development)
            if random.random() < 0.1:  # 10% chance to change status in development
                status_options = {
                    'Processing': 'In Transit',
                    'In Transit': 'Out for Delivery',
                    'Out for Delivery': 'Delivered'
                }
                if tracking_data['status'] in status_options:
                    tracking_data['status'] = status_options[tracking_data['status']]
                    print(f"🔄 Updated {tracking_id} status to: {tracking_data['status']}")
            
            # Save updated data
            data['tracking_ids'][tracking_id] = tracking_data
            save_data(data)
        
        return jsonify({
            'success': True,
            **tracking_data
        })
    
    return jsonify({'success': False, 'error': 'Tracking ID not found'}), 404

# Image upload endpoint
@app.route('/api/tracking/<tracking_id>/image', methods=['POST'])
def upload_tracking_image(tracking_id):
    """Upload image for tracking ID"""
    data = load_data()
    
    if tracking_id not in data['tracking_ids']:
        return jsonify({'success': False, 'error': 'Tracking ID not found'}), 404
    
    # Check if image file is in the request
    if 'image' not in request.files:
        # Check if base64 image data is in JSON
        if request.json and 'image_base64' in request.json:
            try:
                # Decode base64 image
                image_data = request.json['image_base64']
                if ',' in image_data:
                    # Remove data:image/...;base64, prefix
                    image_data = image_data.split(',')[1]
                
                # Convert base64 to bytes
                image_bytes = base64.b64decode(image_data)
                
                # Save image file
                filename = f"{tracking_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(image_bytes)
                
                # Update tracking data
                data['tracking_ids'][tracking_id]['image_url'] = f'/uploads/{filename}'
                data['tracking_ids'][tracking_id]['last_updated'] = str(datetime.now())
                
                # Update stats
                save_data(data)
                
                return jsonify({
                    'success': True, 
                    'message': 'Image uploaded successfully',
                    'image_url': f'/uploads/{filename}',
                    'tracking_id': tracking_id
                })
                
            except Exception as e:
                return jsonify({'success': False, 'error': f'Invalid image data: {str(e)}'}), 400
        
        return jsonify({'success': False, 'error': 'No image provided'}), 400
    
    # Handle file upload
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No image selected'}), 400
    
    if file and allowed_file(file.filename):
        # Save the file
        filename = secure_filename(f"{tracking_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Update tracking data
        data['tracking_ids'][tracking_id]['image_url'] = f'/uploads/{filename}'
        data['tracking_ids'][tracking_id]['last_updated'] = str(datetime.now())
        
        # Save data
        save_data(data)
        
        return jsonify({
            'success': True, 
            'message': 'Image uploaded successfully',
            'image_url': f'/uploads/{filename}',
            'tracking_id': tracking_id
        })
    
    return jsonify({'success': False, 'error': 'Invalid file type. Allowed: PNG, JPG, JPEG, GIF, WEBP'}), 400

# Delete image endpoint
@app.route('/api/tracking/<tracking_id>/image', methods=['DELETE'])
def delete_tracking_image(tracking_id):
    """Delete image for tracking ID"""
    data = load_data()
    
    if tracking_id not in data['tracking_ids']:
        return jsonify({'success': False, 'error': 'Tracking ID not found'}), 404
    
    # Remove image reference
    if 'image_url' in data['tracking_ids'][tracking_id]:
        image_url = data['tracking_ids'][tracking_id].pop('image_url')
        
        # Try to delete the actual file
        try:
            filename = image_url.split('/')[-1]
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"🗑️ Deleted image file: {filename}")
        except Exception as e:
            print(f"⚠️ Could not delete image file: {e}")
        
        data['tracking_ids'][tracking_id]['last_updated'] = str(datetime.now())
        save_data(data)
    
    return jsonify({'success': True, 'message': 'Image deleted successfully'})

# Admin API endpoints
@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    """Admin login endpoint"""
    data = request.json
    if data.get('username') == 'admin' and data.get('password') == 'admin123':
        return jsonify({
            'success': True, 
            'token': 'admin_token',
            'message': 'Login successful',
            'username': 'admin',
            'permissions': ['read', 'write', 'delete', 'configure']
        })
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@app.route('/api/tracking/all', methods=['GET'])
def get_all_tracking():
    """Get all tracking data"""
    data = load_data()
    return jsonify(data['tracking_ids'])

@app.route('/api/tracking/update/<tracking_id>', methods=['PUT'])
def update_tracking(tracking_id):
    """Update tracking information"""
    tracking_data = request.json
    data = load_data()
    
    if tracking_id not in data['tracking_ids']:
        return jsonify({'success': False, 'error': 'Tracking ID not found'}), 404
    
    # Update only allowed fields
    allowed_fields = ['name', 'address', 'city', 'state', 'zip', 'delivery_date', 'status', 'locations']
    for field in allowed_fields:
        if field in tracking_data:
            data['tracking_ids'][tracking_id][field] = tracking_data[field]
    
    data['tracking_ids'][tracking_id]['last_updated'] = str(datetime.now())
    
    save_data(data)
    
    return jsonify({
        'success': True, 
        'message': 'Tracking ID updated successfully',
        'tracking_id': tracking_id
    })

@app.route('/api/tracking/delete/<tracking_id>', methods=['DELETE'])
def delete_tracking(tracking_id):
    """Delete tracking ID"""
    data = load_data()
    
    if tracking_id not in data['tracking_ids']:
        return jsonify({'success': False, 'error': 'Tracking ID not found'}), 404
    
    # Check if there's an image to delete
    if 'image_url' in data['tracking_ids'][tracking_id]:
        try:
            image_url = data['tracking_ids'][tracking_id]['image_url']
            filename = image_url.split('/')[-1]
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                print(f"🗑️ Deleted image file while deleting tracking ID: {filename}")
        except Exception as e:
            print(f"⚠️ Could not delete image file: {e}")
    
    # Store deleted tracking info for logging
    deleted_tracking = data['tracking_ids'][tracking_id]
    del data['tracking_ids'][tracking_id]
    
    save_data(data)
    
    return jsonify({
        'success': True, 
        'message': 'Tracking ID deleted successfully',
        'deleted_tracking': deleted_tracking
    })

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get system statistics"""
    data = load_data()
    
    # Calculate real-time stats
    tracking_ids = data.get('tracking_ids', {})
    
    stats = data.get('system_stats', {})
    
    # Update stats with current values
    stats['total_tracking_ids'] = len(tracking_ids)
    stats['active_shipments'] = sum(
        1 for t in tracking_ids.values() 
        if t.get('status', '') in ['In Transit', 'Processing', 'Out for Delivery']
    )
    stats['delivered_today'] = sum(
        1 for t in tracking_ids.values() 
        if t.get('status', '') == 'Delivered' and 
        t.get('last_updated', '').startswith(str(datetime.now().date()))
    )
    stats['images_count'] = sum(
        1 for t in tracking_ids.values() 
        if t.get('image_url') or t.get('image_base64')
    )
    stats['last_updated'] = str(datetime.now())
    
    # Save updated stats
    data['system_stats'] = stats
    save_data(data)
    
    return jsonify(stats)

@app.route('/api/tracking/add', methods=['POST'])
def add_tracking():
    """Add new tracking ID"""
    tracking_data = request.json
    data = load_data()
    
    # Load system configuration for default location
    config = load_config()
    default_location = config.get('default_location', {
        "city": "Berlin, Germany", 
        "lat": 52.5200, 
        "long": 13.4050
    })
    
    tracking_id = tracking_data.get('tracking_id')
    if not tracking_id or len(tracking_id) != 10:
        return jsonify({'success': False, 'error': 'Tracking ID must be 10 characters'}), 400
    
    if tracking_id in data['tracking_ids']:
        return jsonify({'success': False, 'error': 'Tracking ID already exists'}), 400
    
    # Use custom location if provided, otherwise use default from config
    if 'locations' in tracking_data and tracking_data['locations']:
        # Use the location provided in the request
        locations = tracking_data['locations']
    else:
        # Use the system's default location
        locations = [default_location]
    
    # Set default delivery date if not provided (3 days from now)
    delivery_date = tracking_data.get('delivery_date', 
                                     str((datetime.now().replace(day=datetime.now().day + 3)).date()))
    
    # Create new tracking entry
    new_tracking = {
        'name': tracking_data.get('name', ''),
        'address': tracking_data.get('address', ''),
        'city': tracking_data.get('city', ''),
        'state': tracking_data.get('state', ''),
        'zip': tracking_data.get('zip', ''),
        'delivery_date': delivery_date,
        'status': tracking_data.get('status', 'In Transit'),
        'locations': locations,
        'created_at': str(datetime.now()),
        'last_updated': str(datetime.now())
    }
    
    data['tracking_ids'][tracking_id] = new_tracking
    
    # Save data (which will update stats)
    save_data(data)
    
    return jsonify({
        'success': True, 
        'message': 'Tracking ID added successfully',
        'tracking_id': tracking_id,
        'data': new_tracking
    })

# Backup/Export endpoint
@app.route('/api/export', methods=['GET'])
def export_data():
    """Export all data"""
    data = load_data()
    return jsonify(data)

# Import endpoint
@app.route('/api/import', methods=['POST'])
def import_data():
    """Import data"""
    try:
        import_data = request.json
        
        # Validate data structure
        if not isinstance(import_data, dict):
            return jsonify({'success': False, 'error': 'Invalid data format'}), 400
        
        # If data has tracking_ids key, use that structure
        if 'tracking_ids' in import_data:
            data_to_save = import_data
        else:
            # Assume it's tracking_ids data
            data_to_save = {
                'tracking_ids': import_data,
                'system_stats': load_data().get('system_stats', {})
            }
        
        save_data(data_to_save)
        
        return jsonify({
            'success': True, 
            'message': 'Data imported successfully',
            'imported_count': len(data_to_save.get('tracking_ids', {}))
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# Test endpoint for checking functionality
@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """Test endpoint for debugging"""
    return jsonify({
        'success': True,
        'message': 'API is working',
        'timestamp': str(datetime.now()),
        'base_url': BASE_URL,
        'data_file': os.path.exists(DATA_FILE),
        'config_file': os.path.exists(CONFIG_FILE),
        'uploads_folder': os.path.exists(UPLOAD_FOLDER),
        'python_version': sys.version,
        'flask_version': '2.3.3'
    })

# Reset endpoint (for development only)
@app.route('/api/reset', methods=['POST'])
def reset_data():
    """Reset data to defaults (development only)"""
    if IS_PRODUCTION:
        return jsonify({'success': False, 'error': 'Reset not allowed in production'}), 403
    
    try:
        # Remove existing data files
        for file_path in [DATA_FILE, CONFIG_FILE]:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"🗑️ Deleted: {file_path}")
        
        # Remove uploads (except sample)
        if os.path.exists(UPLOAD_FOLDER):
            for file in os.listdir(UPLOAD_FOLDER):
                if file != 'sample_package.jpg':
                    os.remove(os.path.join(UPLOAD_FOLDER, file))
        
        # Reload fresh data
        load_config()
        load_data()
        
        return jsonify({
            'success': True, 
            'message': 'Data reset successfully',
            'timestamp': str(datetime.now())
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found', 'path': request.path}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

@app.errorhandler(400)
def bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({'error': 'Method not allowed'}), 405

# Main application entry point
if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 SMART REAL-TIME PACKAGE TRACKING SYSTEM")
    print("="*60)
    
    # Load initial data and config
    config = load_config()
    data = load_data()
    
    print(f"\n📍 System Information:")
    print(f"   • Version: {config.get('version', '2.0.0')}")
    print(f"   • Company: {config.get('company_name', 'Package Tracking')}")
    print(f"   • Base URL: {BASE_URL}")
    print(f"   • Deployment: {'Production' if IS_PRODUCTION else 'Development'}")
    
    print(f"\n📊 Initial Data Loaded:")
    print(f"   • Tracking IDs: {len(data.get('tracking_ids', {}))}")
    print(f"   • Active Shipments: {data.get('system_stats', {}).get('active_shipments', 0)}")
    print(f"   • Images: {data.get('system_stats', {}).get('images_count', 0)}")
    
    print(f"\n🌐 Available Endpoints:")
    print(f"   • Main Tracking: {BASE_URL}/")
    print(f"   • Admin Dashboard: {BASE_URL}/admin")
    print(f"   • Location Config: {BASE_URL}/admin/location")
    print(f"   • Health Check: {BASE_URL}/health")
    print(f"   • System Status: {BASE_URL}/api/status")
    print(f"   • Test Endpoint: {BASE_URL}/api/test")
    
    print(f"\n🔑 Admin Credentials:")
    print(f"   • Username: admin")
    print(f"   • Password: admin123")
    
    print(f"\n📦 Sample Tracking IDs:")
    for tracking_id in list(data.get('tracking_ids', {}).keys())[:3]:
        print(f"   • {tracking_id}")
    
    if len(data.get('tracking_ids', {})) > 3:
        print(f"   • ... and {len(data.get('tracking_ids', {})) - 3} more")
    
    print(f"\n📁 Data Files:")
    print(f"   • Tracking Data: {DATA_FILE}")
    print(f"   • Config File: {CONFIG_FILE}")
    print(f"   • Uploads Folder: {UPLOAD_FOLDER}")
    
    print("\n" + "="*60)
    print("✅ System ready! Press Ctrl+C to stop")
    print("="*60 + "\n")

    # Determine port for deployment
    port = int(os.environ.get("PORT", 5000))
    
    # Run the application
    if IS_PRODUCTION:
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        app.run(host='0.0.0.0', port=port, debug=True)
