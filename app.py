from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime
import random
import base64
from werkzeug.utils import secure_filename

<<<<<<< Updated upstream:app.py
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Explicit CORS for all API endpoints
=======
app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)
>>>>>>> Stashed changes:server.py

# Configuration for Render.com
DATA_FILE = os.path.join(os.getcwd(), 'tracking_data.json')
CONFIG_FILE = os.path.join(os.getcwd(), 'system_config.json')
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Create necessary directories
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('templates', exist_ok=True)
os.makedirs('static', exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_base_url():
    # Dynamic base URL for Render.com
    base_url = os.environ.get('RENDER_EXTERNAL_URL') or f"http://127.0.0.1:{os.environ.get('PORT', 5000)}"
    return base_url.rstrip('/')

base_url = get_base_url()

def load_config():
    """Load system configuration"""
    default_config = {
        "default_location": {
            "city": "Berlin, Germany",
            "lat": 52.5200,
            "long": 13.4050
        },
        "company_name": "Package Tracking System",
        "map_zoom_level": 12,
        "base_url": base_url
    }
    
    if not os.path.exists(CONFIG_FILE):
        save_config(default_config)
        return default_config
    
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            # Update base_url if it's old
            config['base_url'] = base_url
            return config
    except:
        return default_config

def save_config(config):
    """Save system configuration"""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)

def load_data():
    if not os.path.exists(DATA_FILE):
<<<<<<< Updated upstream:app.py
=======
        # Load system configuration for default location
        config = load_config()
        default_location = config.get('default_location', {
            "city": "Berlin, Germany", 
            "lat": 52.5200, 
            "long": 13.4050
        })
        
        # Default data structure
>>>>>>> Stashed changes:server.py
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
                    "last_updated": str(datetime.now())
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
                }
            },
            "system_stats": {
                "total_tracking_ids": 2,
                "active_shipments": 2,
                "delivered_today": 0,
                "images_count": 0
            }
        }
        save_data(default_data)
        return default_data
    
<<<<<<< Updated upstream:app.py
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)
        if 'system_stats' not in data:
            data['system_stats'] = {
                'total_tracking_ids': len(data.get('tracking_ids', {})),
                'active_shipments': sum(1 for t in data.get('tracking_ids', {}).values() 
                                       if t.get('status', '') in ['In Transit', 'Processing', 'Out for Delivery']),
                'delivered_today': sum(1 for t in data.get('tracking_ids', {}).values() 
                                      if t.get('status', '') == 'Delivered' and 
                                      t.get('last_updated', '').startswith(str(datetime.now().date()))),
                'images_count': sum(1 for t in data.get('tracking_ids', {}).values() 
                                   if t.get('image_url') or t.get('image_base64') or t.get('has_image'))
            }
            save_data(data)
        return data
=======
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
                                       if t.get('image_url') or t.get('image_base64') or t.get('has_image'))
                }
                save_data(data)
                
            return data
    except:
        return load_config()
>>>>>>> Stashed changes:server.py

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Serve static files
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

# Serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Routes
@app.route('/')
def tracking_page():
<<<<<<< Updated upstream:app.py
    return render_template('tracking.html', api_base=request.host_url.rstrip('/'))

@app.route('/admin')
def admin_page():
    return render_template('admin_dashboard.html', api_base=request.host_url.rstrip('/'))
=======
    config = load_config()
    return render_template('tracking.html', base_url=config.get('base_url', base_url))

@app.route('/admin')
def admin_page():
    config = load_config()
    return render_template('admin_dashboard.html', base_url=config.get('base_url', base_url))

@app.route('/admin/location')
def admin_location_page():
    config = load_config()
    return render_template('admin_location.html', base_url=config.get('base_url', base_url))

# Health check endpoint for Render.com
@app.route('/health')
def health_check():
    return jsonify({'status': 'healthy', 'timestamp': str(datetime.now())})

# System configuration endpoints
@app.route('/api/config', methods=['GET'])
def get_config():
    config = load_config()
    return jsonify(config)

@app.route('/api/config/location', methods=['PUT'])
def update_location():
    # Verify admin access
    auth_header = request.headers.get('Authorization')
    if not auth_header or 'admin_token' not in auth_header:
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
        for tracking_id in data['tracking_ids']:
            if data['tracking_ids'][tracking_id].get('locations'):
                data['tracking_ids'][tracking_id]['locations'][0] = config['default_location']
        save_data(data)
    
    save_config(config)
    
    return jsonify({
        'success': True, 
        'message': 'Default location updated successfully',
        'location': config['default_location']
    })

@app.route('/api/config', methods=['PUT'])
def update_config():
    # Verify admin access
    auth_header = request.headers.get('Authorization')
    if not auth_header or 'admin_token' not in auth_header:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 401
    
    config_data = request.json
    config = load_config()
    
    # Update only allowed fields
    allowed_fields = ['default_location', 'company_name', 'map_zoom_level']
    for field in allowed_fields:
        if field in config_data:
            config[field] = config_data[field]
    
    save_config(config)
    
    return jsonify({'success': True, 'message': 'Configuration updated'})
>>>>>>> Stashed changes:server.py

# API endpoints
@app.route('/api/tracking/<tracking_id>', methods=['GET'])
def get_tracking_info(tracking_id):
    data = load_data()
    if tracking_id in data['tracking_ids']:
        tracking_data = data['tracking_ids'][tracking_id]
        return jsonify({'success': True, **tracking_data})
    return jsonify({'success': False, 'error': 'Tracking ID not found'}), 404

@app.route('/api/tracking/<tracking_id>/status', methods=['GET'])
def get_tracking_status(tracking_id):
    data = load_data()
    if tracking_id in data['tracking_ids']:
        tracking_data = data['tracking_ids'][tracking_id]
        if tracking_data['status'] in ['In Transit', 'Processing', 'Out for Delivery']:
<<<<<<< Updated upstream:app.py
            loc = tracking_data['locations'][0]
            loc['lat'] = round(loc['lat'] + random.uniform(-0.01, 0.01), 4)
            loc['long'] = round(loc['long'] + random.uniform(-0.01, 0.01), 4)
            tracking_data['last_updated'] = str(datetime.now())
            if random.random() < 0.05:
                status_map = {'Processing':'In Transit','In Transit':'Out for Delivery','Out for Delivery':'Delivered'}
                if tracking_data['status'] in status_map:
                    tracking_data['status'] = status_map[tracking_data['status']]
=======
            # Add small random movement to location
            if tracking_data['locations']:
                current_location = tracking_data['locations'][0]
                new_lat = current_location['lat'] + random.uniform(-0.01, 0.01)
                new_long = current_location['long'] + random.uniform(-0.01, 0.01)
                
                tracking_data['locations'][0]['lat'] = round(new_lat, 4)
                tracking_data['locations'][0]['long'] = round(new_long, 4)
                tracking_data['last_updated'] = str(datetime.now())
            
            # Occasionally update status
            if random.random() < 0.05:  # 5% chance to change status
                status_options = {
                    'Processing': 'In Transit',
                    'In Transit': 'Out for Delivery',
                    'Out for Delivery': 'Delivered'
                }
                if tracking_data['status'] in status_options:
                    tracking_data['status'] = status_options[tracking_data['status']]
            
            # Save updated data
>>>>>>> Stashed changes:server.py
            data['tracking_ids'][tracking_id] = tracking_data
            save_data(data)
        return jsonify({'success': True, **tracking_data})
    return jsonify({'success': False, 'error': 'Tracking ID not found'}), 404

@app.route('/api/tracking/<tracking_id>/image', methods=['POST'])
def upload_tracking_image(tracking_id):
    data = load_data()
    if tracking_id not in data['tracking_ids']:
        return jsonify({'success': False, 'error': 'Tracking ID not found'}), 404
    if 'image' not in request.files:
        if request.json and 'image_base64' in request.json:
            try:
                img_data = request.json['image_base64'].split(',')[-1]
                img_bytes = base64.b64decode(img_data)
                filename = f"{tracking_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                with open(filepath, 'wb') as f:
                    f.write(img_bytes)
                data['tracking_ids'][tracking_id]['image_url'] = f'/uploads/{filename}'
                data['tracking_ids'][tracking_id]['last_updated'] = str(datetime.now())
                save_data(data)
                return jsonify({'success': True, 'message': 'Image uploaded successfully', 'image_url': f'/uploads/{filename}'})
            except Exception as e:
                return jsonify({'success': False, 'error': f'Invalid image data: {str(e)}'}), 400
        return jsonify({'success': False, 'error': 'No image provided'}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No image selected'}), 400
    if file and allowed_file(file.filename):
        filename = secure_filename(f"{tracking_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{file.filename}")
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        data['tracking_ids'][tracking_id]['image_url'] = f'/uploads/{filename}'
        data['tracking_ids'][tracking_id]['last_updated'] = str(datetime.now())
        save_data(data)
        return jsonify({'success': True, 'message': 'Image uploaded successfully', 'image_url': f'/uploads/{filename}'})
    return jsonify({'success': False, 'error': 'Invalid file type'}), 400

@app.route('/api/tracking/<tracking_id>/image', methods=['DELETE'])
def delete_tracking_image(tracking_id):
    data = load_data()
    if tracking_id not in data['tracking_ids']:
        return jsonify({'success': False, 'error': 'Tracking ID not found'}), 404
    if 'image_url' in data['tracking_ids'][tracking_id]:
        image_url = data['tracking_ids'][tracking_id].pop('image_url')
        try:
            filepath = os.path.join(UPLOAD_FOLDER, image_url.split('/')[-1])
            if os.path.exists(filepath): os.remove(filepath)
        except: pass
        data['tracking_ids'][tracking_id]['last_updated'] = str(datetime.now())
        save_data(data)
    return jsonify({'success': True, 'message': 'Image deleted successfully'})

@app.route('/api/admin/login', methods=['POST'])
def admin_login():
    creds = request.json
    if creds.get('username') == 'admin' and creds.get('password') == 'admin123':
        return jsonify({'success': True, 'token': 'admin_token'})
    return jsonify({'success': False, 'error': 'Invalid credentials'}), 401

@app.route('/api/tracking/all', methods=['GET'])
def get_all_tracking():
    return jsonify(load_data()['tracking_ids'])

@app.route('/api/tracking/update/<tracking_id>', methods=['PUT'])
def update_tracking(tracking_id):
    tracking_data = request.json
    data = load_data()
    if tracking_id not in data['tracking_ids']:
        return jsonify({'success': False, 'error': 'Tracking ID not found'}), 404
    allowed_fields = ['name','address','city','state','zip','delivery_date','status','locations']
    for f in allowed_fields:
        if f in tracking_data:
            data['tracking_ids'][tracking_id][f] = tracking_data[f]
    data['tracking_ids'][tracking_id]['last_updated'] = str(datetime.now())
    save_data(data)
    return jsonify({'success': True, 'message': 'Tracking ID updated'})

@app.route('/api/tracking/delete/<tracking_id>', methods=['DELETE'])
def delete_tracking(tracking_id):
    data = load_data()
    if tracking_id not in data['tracking_ids']:
        return jsonify({'success': False, 'error': 'Tracking ID not found'}), 404
    if 'image_url' in data['tracking_ids'][tracking_id]:
        try:
            filepath = os.path.join(UPLOAD_FOLDER, data['tracking_ids'][tracking_id]['image_url'].split('/')[-1])
            if os.path.exists(filepath): os.remove(filepath)
        except: pass
    del data['tracking_ids'][tracking_id]
    save_data(data)
    return jsonify({'success': True, 'message': 'Tracking ID deleted'})

@app.route('/api/stats', methods=['GET'])
def get_stats():
    data = load_data()
    tracking_ids = data.get('tracking_ids', {})
    stats = data.get('system_stats', {})
    stats['total_tracking_ids'] = len(tracking_ids)
    stats['active_shipments'] = sum(1 for t in tracking_ids.values() if t['status'] in ['In Transit','Processing','Out for Delivery'])
    stats['delivered_today'] = sum(1 for t in tracking_ids.values() if t['status']=='Delivered' and t['last_updated'].startswith(str(datetime.now().date())))
    stats['images_count'] = sum(1 for t in tracking_ids.values() if t.get('image_url'))
    data['system_stats'] = stats
    save_data(data)
    return jsonify(stats)

<<<<<<< Updated upstream:app.py
=======
# Fix the add_tracking function to use configurable location
>>>>>>> Stashed changes:server.py
@app.route('/api/tracking/add', methods=['POST'])
def add_tracking():
    tracking_data = request.json
    data = load_data()
<<<<<<< Updated upstream:app.py
    tracking_id = tracking_data.get('tracking_id')
    if not tracking_id or len(tracking_id)!=10: return jsonify({'success': False, 'error': 'Tracking ID must be 10 chars'}),400
    if tracking_id in data['tracking_ids']: return jsonify({'success': False, 'error':'Tracking ID exists'}),400
=======
    
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
    
    # Set default delivery date if not provided
>>>>>>> Stashed changes:server.py
    delivery_date = tracking_data.get('delivery_date', str(datetime.now().date()))
    data['tracking_ids'][tracking_id] = {
        'name': tracking_data.get('name',''),
        'address': tracking_data.get('address',''),
        'city': tracking_data.get('city',''),
        'state': tracking_data.get('state',''),
        'zip': tracking_data.get('zip',''),
        'delivery_date': delivery_date,
<<<<<<< Updated upstream:app.py
        'status': tracking_data.get('status','In Transit'),
        'locations': tracking_data.get('locations',[{"city":"Berlin, Germany","lat":52.52,"long":13.405}]),
=======
        'status': tracking_data.get('status', 'In Transit'),
        'locations': locations,  # Use the location variable we set above
>>>>>>> Stashed changes:server.py
        'created_at': str(datetime.now()),
        'last_updated': str(datetime.now())
    }
    save_data(data)
    return jsonify({'success': True, 'message': 'Tracking ID added'})

# Backup/Export endpoint
@app.route('/api/export', methods=['GET'])
def export_data():
    data = load_data()
    return jsonify(data)

# Import endpoint
@app.route('/api/import', methods=['POST'])
def import_data():
    try:
        data = request.json
        save_data(data)
        return jsonify({'success': True, 'message': 'Data imported successfully'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    print("🚀 Starting Package Tracking System with Image Upload...")
<<<<<<< Updated upstream:app.py
    print(f"📍 Tracking Page: http://localhost:5000")
    print(f"👑 Admin Panel: http://localhost:5000/admin")
    print(f"🔑 Admin Login: username=admin, password=admin123")
    print("📸 Images will be saved to: uploads/")
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)
=======
    print(f"📍 Base URL: {base_url}")
    print("👑 Admin Panel: /admin")
    print("📍 Location Configuration: /admin/location")
    print("🔑 Admin Login: username=admin, password=admin123")
    print("📦 Sample Tracking IDs: AB123CDE45, JGD987WQTR")
    print("📸 Images will be saved to: uploads/")
    print("\nPress Ctrl+C to stop the server")

    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)  # debug=False for production
>>>>>>> Stashed changes:server.py
