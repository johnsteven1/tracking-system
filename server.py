from flask import Flask, jsonify, request, render_template, send_from_directory
from flask_cors import CORS
import json
import os
from datetime import datetime
import random
import base64
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})  # Explicit CORS for all API endpoints

# Configuration
DATA_FILE = 'tracking_data.json'
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_data():
    if not os.path.exists(DATA_FILE):
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
        save_data(default_data)
        return default_data
    
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

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=4)

# Serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

# Routes
@app.route('/')
def tracking_page():
    return render_template('tracking.html', api_base=request.host_url.rstrip('/'))

@app.route('/admin')
def admin_page():
    return render_template('admin_dashboard.html', api_base=request.host_url.rstrip('/'))

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
            loc = tracking_data['locations'][0]
            loc['lat'] = round(loc['lat'] + random.uniform(-0.01, 0.01), 4)
            loc['long'] = round(loc['long'] + random.uniform(-0.01, 0.01), 4)
            tracking_data['last_updated'] = str(datetime.now())
            if random.random() < 0.05:
                status_map = {'Processing':'In Transit','In Transit':'Out for Delivery','Out for Delivery':'Delivered'}
                if tracking_data['status'] in status_map:
                    tracking_data['status'] = status_map[tracking_data['status']]
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

@app.route('/api/tracking/add', methods=['POST'])
def add_tracking():
    tracking_data = request.json
    data = load_data()
    tracking_id = tracking_data.get('tracking_id')
    if not tracking_id or len(tracking_id)!=10: return jsonify({'success': False, 'error': 'Tracking ID must be 10 chars'}),400
    if tracking_id in data['tracking_ids']: return jsonify({'success': False, 'error':'Tracking ID exists'}),400
    delivery_date = tracking_data.get('delivery_date', str(datetime.now().date()))
    data['tracking_ids'][tracking_id] = {
        'name': tracking_data.get('name',''),
        'address': tracking_data.get('address',''),
        'city': tracking_data.get('city',''),
        'state': tracking_data.get('state',''),
        'zip': tracking_data.get('zip',''),
        'delivery_date': delivery_date,
        'status': tracking_data.get('status','In Transit'),
        'locations': tracking_data.get('locations',[{"city":"Berlin, Germany","lat":52.52,"long":13.405}]),
        'created_at': str(datetime.now()),
        'last_updated': str(datetime.now())
    }
    save_data(data)
    return jsonify({'success': True, 'message': 'Tracking ID added'})

if __name__ == '__main__':
    print("🚀 Starting Package Tracking System with Image Upload...")
    print(f"📍 Tracking Page: http://localhost:5000")
    print(f"👑 Admin Panel: http://localhost:5000/admin")
    print(f"🔑 Admin Login: username=admin, password=admin123")
    print("📸 Images will be saved to: uploads/")
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)), debug=True)
